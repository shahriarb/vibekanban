"""
Metrics controller for handling DORA metrics-related routes.
"""
from typing import Dict, List, Tuple, Union
from datetime import datetime, timedelta
import numpy as np
from flask import Blueprint, jsonify, request, render_template, current_app
from app import db
from app.models.metric import Metric
from app.models.ticket import Ticket, TicketState, TicketType
from sqlalchemy import func

bp = Blueprint('metrics', __name__, url_prefix='/metrics')

@bp.route('/', methods=['GET'])
def get_metrics() -> Union[str, Dict]:
    """
    Get metrics data.
    
    Returns:
        If requested as JSON, returns a JSON response with metrics data.
        If requested as HTML, returns the metrics dashboard HTML page.
    """
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        # API request, return JSON with all metrics
        return get_all_metrics()
    
    # Web request, return the dashboard HTML
    return render_template('metrics/dashboard.html')

@bp.route('/dashboard', methods=['GET'])
def dashboard() -> str:
    """
    Render the metrics dashboard page.
    
    Returns:
        The rendered HTML template for the metrics dashboard.
    """
    return render_template('metrics/dashboard.html')

@bp.route('/lead-time', methods=['GET'])
def get_lead_time() -> Dict:
    """
    Get lead time metrics based on story tickets.
    
    Lead time is calculated as the time between story creation
    and completion for all completed story tickets.
    
    Returns:
        A JSON response with lead time metrics.
    """
    # Get the story type and done state
    story_type = TicketType.query.filter_by(name='story').first()
    done_state = TicketState.query.filter_by(name='done').first()
    
    if not story_type or not done_state:
        return jsonify({
            'mean': 0,
            'median': 0,
            'p90': 0,
            'min': 0,
            'max': 0,
            'unit': 'minutes',
            'sample_size': 0
        })
    
    # Get all completed story tickets
    story_tickets = Ticket.query.filter_by(
        type=story_type.id,
        state=done_state.id
    ).all()
    
    # Calculate lead times
    lead_times = []
    for ticket in story_tickets:
        if ticket.created_date and ticket.completed_date:
            lead_time = int((ticket.completed_date - ticket.created_date).total_seconds() / 60)
            lead_times.append(lead_time)
            if lead_time > 7000:  # Debug log for tickets taking more than 7000 minutes
                print(f"Long running ticket found - ID: {ticket.id}, Title: {ticket.what}, "
                      f"Created: {ticket.created_date}, Completed: {ticket.completed_date}, "
                      f"Lead Time: {lead_time} minutes")
    
    # Calculate statistics
    if lead_times:
        stats = {
            'mean': round(np.mean(lead_times), 2),
            'median': round(np.median(lead_times), 2),
            'p90': round(np.percentile(lead_times, 90), 2),
            'min': min(lead_times),
            'max': max(lead_times),
            'unit': 'minutes',
            'sample_size': len(lead_times)
        }
    else:
        stats = {
            'mean': 0,
            'median': 0,
            'p90': 0,
            'min': 0,
            'max': 0,
            'unit': 'minutes',
            'sample_size': 0
        }
    
    return jsonify(stats)

@bp.route('/change-failure-rate', methods=['GET'])
def get_change_failure_rate() -> Dict:
    """
    Get change failure rate metrics based on bug tickets.
    
    The change failure rate is calculated as the percentage of bug tickets
    out of total tickets.
    
    Returns:
        A JSON response with change failure rate metrics.
    """
    # Get the bug type
    bug_type = TicketType.query.filter_by(name='bug').first()
    if not bug_type:
        return jsonify({
            'total_deployments': 0,
            'failures': 0,
            'failure_rate_percentage': 0
        })
    
    # Get total count of tickets and count of bug tickets
    total_count = Ticket.query.count()
    bug_count = Ticket.query.filter_by(type=bug_type.id).count()
    
    if total_count > 0:
        failure_rate = round((bug_count / total_count) * 100, 2)
    else:
        failure_rate = 0
    
    stats = {
        'total_deployments': total_count,
        'failures': bug_count,
        'failure_rate_percentage': failure_rate
    }
    
    return jsonify(stats)

@bp.route('/time-to-restore', methods=['GET'])
def get_time_to_restore() -> Dict:
    """
    Get time to restore service metrics based on bug fix time.
    
    Time to restore is calculated as the time between bug creation
    and completion for all completed bug tickets.
    
    Returns:
        A JSON response with time to restore service metrics.
    """
    # Get the bug type and done state
    bug_type = TicketType.query.filter_by(name='bug').first()
    done_state = TicketState.query.filter_by(name='done').first()
    
    if not bug_type or not done_state:
        return jsonify({
            'mean': 0,
            'median': 0,
            'p90': 0,
            'min': 0,
            'max': 0,
            'unit': 'minutes',
            'sample_size': 0
        })
    
    # Get all completed bug tickets
    bug_tickets = Ticket.query.filter_by(
        type=bug_type.id,
        state=done_state.id
    ).all()
    
    # Calculate restoration times
    restore_times = []
    for ticket in bug_tickets:
        if ticket.created_date and ticket.completed_date:
            restore_time = int((ticket.completed_date - ticket.created_date).total_seconds() / 60)
            restore_times.append(restore_time)
    
    # Calculate statistics
    if restore_times:
        stats = {
            'mean': round(np.mean(restore_times), 2),
            'median': round(np.median(restore_times), 2),
            'p90': round(np.percentile(restore_times, 90), 2),
            'min': min(restore_times),
            'max': max(restore_times),
            'unit': 'minutes',
            'sample_size': len(restore_times)
        }
    else:
        stats = {
            'mean': 0,
            'median': 0,
            'p90': 0,
            'min': 0,
            'max': 0,
            'unit': 'minutes',
            'sample_size': 0
        }
    
    return jsonify(stats)

@bp.route('/report-failure', methods=['POST'])
def report_failure() -> Dict:
    """
    Report a failure for a deployed ticket.
    
    Returns:
        A JSON response confirming the failure report.
    """
    data = request.get_json()
    
    # Validate required fields
    if not data.get('ticket_id'):
        return jsonify({'error': 'Ticket ID is required'}), 400
    
    # Check if the ticket exists
    ticket = Ticket.query.get(data['ticket_id'])
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    # Find or create a metric record for this ticket
    metric = Metric.query.filter_by(ticket_id=ticket.id).first()
    
    if not metric:
        # Create a new metric record
        metric = Metric(
            ticket_id=ticket.id,
            change_failure=True,
            restoration_time=data.get('restoration_time'),
            deployment_date=data.get('deployment_date', datetime.utcnow())
        )
        db.session.add(metric)
    else:
        # Update existing metric record
        metric.change_failure = True
        if 'restoration_time' in data:
            metric.restoration_time = data['restoration_time']
        if 'deployment_date' in data:
            metric.deployment_date = data['deployment_date']
    
    db.session.commit()
    
    return jsonify(metric.to_dict())

def get_all_metrics() -> Dict:
    """
    Get all metrics data.
    
    Returns:
        A JSON response with comprehensive metrics data.
    """
    lead_time_stats = get_lead_time().get_json()
    failure_rate_stats = get_change_failure_rate().get_json()
    restore_time_stats = get_time_to_restore().get_json()
    
    # Get ticket completion rate
    total_tickets = Ticket.query.count()
    done_state = TicketState.query.filter_by(name='done').first()
    
    if done_state:
        completed_tickets = Ticket.query.filter_by(state=done_state.id).count()
    else:
        completed_tickets = 0
    
    if total_tickets > 0:
        completion_rate = round((completed_tickets / total_tickets) * 100, 2)
    else:
        completion_rate = 0
    
    completion_stats = {
        'total_tickets': total_tickets,
        'completed_tickets': completed_tickets,
        'completion_rate_percentage': completion_rate
    }
    
    return jsonify({
        'lead_time': lead_time_stats,
        'change_failure_rate': failure_rate_stats,
        'time_to_restore': restore_time_stats,
        'completion_rate': completion_stats
    })

@bp.route('/update-historical-bug-metrics', methods=['POST'])
def update_historical_bug_metrics() -> Dict:
    """
    Update metrics for historical bug tickets to mark them as failures.
    
    This is used to ensure all historical bug tickets that are completed
    are properly counted in change failure rate and time to restore metrics.
    
    Returns:
        A JSON response with the results of the update operation.
    """
    # Get the 'bug' type and 'done' state
    bug_type = TicketType.query.filter_by(name='bug').first()
    done_state = TicketState.query.filter_by(name='done').first()
    
    if not bug_type or not done_state:
        return jsonify({
            'status': 'error',
            'message': 'Bug type or Done state not found in the system',
            'updated': 0
        }), 400
    
    # Find all completed bug tickets
    bug_tickets = Ticket.query.filter_by(
        type=bug_type.id,
        state=done_state.id
    ).all()
    
    updated_count = 0
    
    for ticket in bug_tickets:
        # Skip tickets without completion date
        if not ticket.completed_date:
            continue
            
        # Calculate lead time (restoration time for bugs)
        lead_time = None
        if ticket.created_date and ticket.completed_date:
            lead_time = int((ticket.completed_date - ticket.created_date).total_seconds() / 60)
        
        # Check if a metric already exists for this ticket
        metric = Metric.query.filter_by(ticket_id=ticket.id).first()
        
        if metric:
            # Update existing metric
            if not metric.change_failure:
                metric.change_failure = True
                updated_count += 1
            
            if not metric.restoration_time and lead_time:
                metric.restoration_time = lead_time
        else:
            # Create new metric
            metric = Metric(
                ticket_id=ticket.id,
                lead_time=lead_time,
                change_failure=True,
                deployment_date=ticket.completed_date,
                restoration_time=lead_time
            )
            db.session.add(metric)
            updated_count += 1
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': f'Updated metrics for {updated_count} historical bug tickets',
        'updated': updated_count
    })

@bp.route('/longest-story', methods=['GET'])
def get_longest_story() -> Dict:
    """
    Find the story ticket that took the longest time to complete.
    
    Returns:
        A JSON response with the ticket details and completion time.
    """
    # Get the story type and done state
    story_type = TicketType.query.filter_by(name='story').first()
    done_state = TicketState.query.filter_by(name='done').first()
    
    if not story_type or not done_state:
        return jsonify({
            'error': 'Story type or Done state not found'
        }), 404
    
    # Get all completed story tickets
    story_tickets = Ticket.query.filter_by(
        type=story_type.id,
        state=done_state.id
    ).all()
    
    # Find the ticket with the longest lead time
    longest_time = 0
    longest_ticket = None
    
    for ticket in story_tickets:
        if ticket.created_date and ticket.completed_date:
            lead_time = int((ticket.completed_date - ticket.created_date).total_seconds() / 60)
            if lead_time > longest_time:
                longest_time = lead_time
                longest_ticket = ticket
    
    if longest_ticket:
        return jsonify({
            'ticket_id': longest_ticket.id,
            'what': longest_ticket.what,
            'why': longest_ticket.why,
            'created_date': longest_ticket.created_date.isoformat(),
            'completed_date': longest_ticket.completed_date.isoformat(),
            'lead_time_minutes': longest_time,
            'lead_time_days': round(longest_time / (24 * 60), 2)
        })
    else:
        return jsonify({
            'error': 'No completed story tickets found'
        }), 404 