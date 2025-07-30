
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2 import service_account
from typing import Dict, Any

class GoogleCalendar:
    """
    A class to handle Google Calendar operations including authentication, event management,
    and availability checking.
    """
    
    def __init__(self, tool_config: Dict[str, Any]):
        """
        Initialize Google Calendar service.
        
        Args:
            credentials_path (str): Path to the service account credentials JSON file.
        """
        self.tool_config = tool_config
        self.credentials_path = tool_config.get("credentials_path")
        self.CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/calendar.events"]
        self.calendar_service = self._get_calendar_service(self.credentials_path)

    def _get_calendar_service(self):
        """
        Get or create Google Calendar service with proper authentication.
        
        Returns:
            googleapiclient.discovery.Resource: Authenticated Google Calendar service
        """
        if not self.credentials_path:
            raise FileNotFoundError(f"Service account credentials file not found: {self.credentials_path}")

        creds = service_account.Credentials.from_service_account_file(
            self.credentials_path, scopes=self.CALENDAR_SCOPES
        )

        return build("calendar", "v3", credentials=creds)

    def check_slot_availability(self, start_time, duration_minutes=60):
        """
        Check if a time slot is available in the calendar.
        
        Args:
            start_time (datetime): Start time of the slot to check
            duration_minutes (int): Duration of the slot in minutes
            
        Returns:
            bool: True if slot is available, False otherwise
        """
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        events_result = self.calendar_service.events().list(
            calendarId='primary',
            timeMin=start_time.isoformat() + 'Z',
            timeMax=end_time.isoformat() + 'Z',
            singleEvents=True
        ).execute()
        
        events = events_result.get('items', [])
        return len(events) == 0

    def get_available_slots(self, start_date, end_date, duration_minutes=60):
        """
        Get list of available time slots between two dates.
        
        Args:
            start_date (datetime): Start date to check from
            end_date (datetime): End date to check until
            duration_minutes (int): Duration of each slot
            
        Returns:
            list: List of available datetime slots
        """
        events_result = self.calendar_service.events().list(
            calendarId='primary',
            timeMin=start_date.isoformat() + 'Z',
            timeMax=end_date.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Convert events to busy periods
        busy_periods = []
        for event in events:
            start = datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')))
            end = datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date')))
            busy_periods.append((start, end))
        
        # Find available slots
        available_slots = []
        current_time = start_date
        
        while current_time < end_date:
            slot_end = current_time + timedelta(minutes=duration_minutes)
            is_available = True
            
            for busy_start, busy_end in busy_periods:
                if (current_time < busy_end and slot_end > busy_start):
                    is_available = False
                    break
            
            if is_available:
                available_slots.append(current_time)
            
            current_time += timedelta(minutes=30)  # Check every 30 minutes
        
        return available_slots

    def delete_event(self, event_id):
        """
        Delete a calendar event.
        
        Args:
            event_id (str): ID of the event to delete
        """
        return self.calendar_service.events().delete(
            calendarId='primary',
            eventId=event_id
        ).execute()

    def create_event(self, summary, description, start_time, end_time, attendees=None, timezone='UTC'):
        """
        Create a calendar event.
        
        Args:
            summary (str): Event title
            description (str): Event description
            start_time (datetime): Event start time
            end_time (datetime): Event end time
            attendees (list, optional): List of attendee email addresses (Note: Currently not supported with service account)
            timezone (str): Timezone for the event
        """
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': timezone,
            }
        }

        event_result = self.calendar_service.events().insert(
            calendarId='primary',
            body=event
        ).execute()

        return {
            'event_id': event_result.get('id'),
            'status': event_result.get('status', 'confirmed')
        } 