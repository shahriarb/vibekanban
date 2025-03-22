"""
Metrics controller for handling DORA metrics-related routes.
"""
from typing import Dict, List, Tuple, Union
from datetime import datetime, timedelta
import numpy as np
from flask import Blueprint, jsonify, request, render_template, current_app
from app import db
from app.models.metric import Metric
from app.models.ticket import Ticket, TicketState
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
    Get lead time metrics.
    
    Returns:
        A JSON response with lead time metrics.
    """
    # Get all metrics with lead time data
    metrics = Metric.query.filter(Metric.lead_time.isnot(None)).all()
    
    # Calculate mean, median, p90, min, max
    if metrics:
        lead_times = [m.lead_time for m in metrics]
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

@bp.route('/deployment-frequency', methods=['GET'])
def get_deployment_frequency() -> Dict:
    """
    Get deployment frequency metrics.
    
    Returns:
        A JSON response with deployment frequency metrics.
    """
    # Get count of deployments in the last day, week, and month
    now = datetime.utcnow()
    day_ago = now - timedelta(days=1)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    daily_count = Metric.query.filter(Metric.deployment_date >= day_ago).count()
    weekly_count = Metric.query.filter(Metric.deployment_date >= week_ago).count()
    monthly_count = Metric.query.filter(Metric.deployment_date >= month_ago).count()
    
    stats = {
        'daily': daily_count,
        'weekly': weekly_count,
        'monthly': monthly_count,
        'daily_avg': round(daily_count / 1, 2),
        'weekly_avg': round(weekly_count / 7, 2),
        'monthly_avg': round(monthly_count / 30, 2)
    }
    
    return jsonify(stats)

@bp.route('/change-failure-rate', methods=['GET'])
def get_change_failure_rate() -> Dict:
    """
    Get change failure rate metrics.
    
    Returns:
        A JSON response with change failure rate metrics.
    """
    # Get total count of deployments and count of failures
    total_count = Metric.query.filter(Metric.deployment_date.isnot(None)).count()
    failure_count = Metric.query.filter(Metric.change_failure == True).count()
    
    if total_count > 0:
        failure_rate = round((failure_count / total_count) * 100, 2)
    else:
        failure_rate = 0
    
    stats = {
        'total_deployments': total_count,
        'failures': failure_count,
        'failure_rate_percentage': failure_rate
    }
    
    return jsonify(stats)

@bp.route('/time-to-restore', methods=['GET'])
def get_time_to_restore() -> Dict:
    """
    Get time to restore service metrics.
    
    Returns:
        A JSON response with time to restore service metrics.
    """
    # Get all metrics with restoration time data
    metrics = Metric.query.filter(
        Metric.restoration_time.isnot(None),
        Metric.change_failure == True
    ).all()
    
    # Calculate mean, median, p90, min, max
    if metrics:
        restore_times = [m.restoration_time for m in metrics]
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
    deployment_freq_stats = get_deployment_frequency().get_json()
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
        'deployment_frequency': deployment_freq_stats,
        'change_failure_rate': failure_rate_stats,
        'time_to_restore': restore_time_stats,
        'completion_rate': completion_stats
    }) 