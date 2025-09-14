"""
Ticket models for the Kanban board application.
"""

from typing import Dict, List, Optional
from datetime import datetime
from app import db

# Ticket dependencies association table
ticket_dependencies = db.Table(
    "ticket_dependencies",
    db.Column(
        "dependent_id", db.Integer, db.ForeignKey("tickets.id"), primary_key=True
    ),
    db.Column(
        "dependency_id", db.Integer, db.ForeignKey("tickets.id"), primary_key=True
    ),
    db.Column("created_date", db.DateTime, default=datetime.utcnow),
)


class TicketType(db.Model):  # type: ignore
    """
    Ticket type model representing the different types a ticket can have.

    Attributes:
        id: The unique identifier for the ticket type.
        name: The name of the ticket type (e.g., 'bug', 'story', 'spike').
    """

    __tablename__ = "ticket_types"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    tickets = db.relationship("Ticket", backref="type_info", lazy=True)

    def to_dict(self) -> Dict:
        """
        Convert the ticket type to a dictionary.

        Returns:
            Dict: A dictionary representation of the ticket type.
        """
        return {"id": self.id, "name": self.name}


class TicketPriority(db.Model):  # type: ignore
    """
    Ticket priority model representing the different priority levels a ticket can have.

    Attributes:
        id: The unique identifier for the ticket priority.
        name: The name of the ticket priority (e.g., 'low', 'medium', 'high', 'critical').
    """

    __tablename__ = "ticket_priorities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    tickets = db.relationship("Ticket", backref="priority_info", lazy=True)

    def to_dict(self) -> Dict:
        """
        Convert the ticket priority to a dictionary.

        Returns:
            Dict: A dictionary representation of the ticket priority.
        """
        return {"id": self.id, "name": self.name}


class TicketState(db.Model):  # type: ignore
    """
    Ticket state model representing the different states a ticket can be in.

    Attributes:
        id: The unique identifier for the ticket state.
        name: The name of the ticket state (e.g., 'backlog', 'in progress', 'done').
    """

    __tablename__ = "ticket_states"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    tickets = db.relationship("Ticket", backref="state_info", lazy=True)

    def to_dict(self) -> Dict:
        """
        Convert the ticket state to a dictionary.

        Returns:
            Dict: A dictionary representation of the ticket state.
        """
        return {"id": self.id, "name": self.name}


class Ticket(db.Model):  # type: ignore
    """
    Ticket model representing a task in the Kanban board.

    Attributes:
        id: The unique identifier for the ticket.
        project_id: The ID of the project this ticket belongs to.
        type: The ID of the ticket type.
        priority: The ID of the ticket priority.
        state: The ID of the ticket state.
        what: Description of what the ticket is about.
        why: Explanation of why this ticket is important.
        acceptance_criteria: Criteria for considering this ticket done.
        test_steps: Steps to test this ticket's functionality.
        created_date: The date and time when the ticket was created.
        completed_date: The date and time when the ticket was completed.
        metrics: List of metrics associated with this ticket.
        attachments: List of attachments associated with this ticket.
        comments: List of comments associated with this ticket.
        dependencies: List of tickets that this ticket depends on.
        dependents: List of tickets that depend on this ticket.
    """

    __tablename__ = "tickets"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    type = db.Column(db.Integer, db.ForeignKey("ticket_types.id"), nullable=False)
    priority = db.Column(
        db.Integer, db.ForeignKey("ticket_priorities.id"), nullable=True
    )
    state = db.Column(db.Integer, db.ForeignKey("ticket_states.id"), nullable=False)
    what = db.Column(db.Text, nullable=False)
    why = db.Column(db.Text, nullable=True)
    acceptance_criteria = db.Column(db.Text, nullable=True)
    test_steps = db.Column(db.Text, nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    completed_date = db.Column(db.DateTime, nullable=True)

    # Relationship with metrics
    metrics = db.relationship(
        "Metric", backref="ticket", lazy=True, cascade="all, delete-orphan"
    )

    # Relationship with attachments
    attachments = db.relationship(
        "Attachment", backref="ticket", lazy=True, cascade="all, delete-orphan"
    )

    # Relationship with comments
    comments = db.relationship(
        "Comment", back_populates="ticket", lazy=True, cascade="all, delete-orphan"
    )

    # Self-referential many-to-many relationship for dependencies
    dependencies = db.relationship(
        "Ticket",
        secondary=ticket_dependencies,
        primaryjoin=(ticket_dependencies.c.dependent_id == id),
        secondaryjoin=(ticket_dependencies.c.dependency_id == id),
        backref=db.backref("dependents", lazy="dynamic"),
        lazy="dynamic",
    )

    def to_dict(self) -> Dict:
        """
        Convert the ticket to a dictionary.

        Returns:
            Dict: A dictionary representation of the ticket.
        """
        # Get dependencies and dependents
        dependencies_list = [
            {
                "id": t.id,
                "what": t.what,
                "state": t.state,
                "state_name": t.state_info.name if t.state_info else None,
            }
            for t in self.dependencies.all()
        ]

        dependents_list = [
            {
                "id": t.id,
                "what": t.what,
                "state": t.state,
                "state_name": t.state_info.name if t.state_info else None,
            }
            for t in self.dependents
        ]

        # Calculate if all dependencies are resolved (completed)
        all_dependencies_resolved = (
            all(
                t.state_info and t.state_info.name == "done"
                for t in self.dependencies.all()
            )
            if self.dependencies.count() > 0
            else True
        )

        return {
            "id": self.id,
            "project_id": self.project_id,
            "type": self.type,
            "type_name": self.type_info.name if self.type_info else None,
            "priority": self.priority,
            "priority_name": self.priority_info.name if self.priority_info else None,
            "state": self.state,
            "state_name": self.state_info.name if self.state_info else None,
            "what": self.what,
            "why": self.why,
            "acceptance_criteria": self.acceptance_criteria,
            "test_steps": self.test_steps,
            "created_date": (
                self.created_date.isoformat() if self.created_date else None
            ),
            "completed_date": (
                self.completed_date.isoformat() if self.completed_date else None
            ),
            "attachments": (
                [attachment.to_dict() for attachment in list(self.attachments)]
                if self.attachments
                else []
            ),
            "dependencies": dependencies_list,
            "dependents": dependents_list,
            "all_dependencies_resolved": all_dependencies_resolved,
        }

    @staticmethod
    def from_dict(data: Dict) -> "Ticket":
        """
        Create a new Ticket instance from a dictionary.

        Args:
            data: Dictionary containing ticket data.

        Returns:
            Ticket: A new Ticket instance.
        """
        return Ticket(
            project_id=data.get("project_id"),
            type=data.get("type"),
            priority=data.get("priority"),
            state=data.get("state"),
            what=data.get("what"),
            why=data.get("why"),
            acceptance_criteria=data.get("acceptance_criteria"),
            test_steps=data.get("test_steps"),
        )

    def update_state(self, new_state_id: int) -> None:
        """
        Update the state of the ticket and set completed_date if moved to 'done'.

        Args:
            new_state_id: The ID of the new state.
        """
        self.state = new_state_id

        # Check if the new state is 'done'
        state = TicketState.query.get(new_state_id)
        if state and state.name == "done":
            # Set the completed date when moved to 'done'
            if not self.completed_date:
                self.completed_date = datetime.utcnow()
        # Reset completed date if moved away from 'done'
        # No special handling needed for 'on hold' state
        # as it doesn't affect the completed_date
        else:
            self.completed_date = None

    def add_dependency(self, ticket: "Ticket") -> None:
        """
        Add a dependency to this ticket.

        Args:
            ticket: The ticket that this ticket depends on.
        """
        if ticket.id != self.id and not self.has_dependency(ticket):
            self.dependencies.append(ticket)

    def remove_dependency(self, ticket: "Ticket") -> None:
        """
        Remove a dependency from this ticket.

        Args:
            ticket: The ticket to remove as a dependency.
        """
        if self.has_dependency(ticket):
            self.dependencies.remove(ticket)

    def has_dependency(self, ticket: "Ticket") -> bool:
        """
        Check if this ticket depends on the given ticket.

        Args:
            ticket: The ticket to check as a dependency.

        Returns:
            bool: True if this ticket depends on the given ticket, False otherwise.
        """
        return self.dependencies.filter(Ticket.id == ticket.id).count() > 0

    def get_all_dependencies_resolved(self) -> bool:
        """
        Check if all dependencies of this ticket are resolved (in 'done' state).

        Returns:
            bool: True if all dependencies are resolved, False otherwise.
        """
        # If there are no dependencies, return True
        if self.dependencies.count() == 0:
            return True

        # Check if all dependencies are resolved
        for dependency in self.dependencies.all():
            state = TicketState.query.get(dependency.state)
            if not state or state.name != "done":
                return False

        return True
