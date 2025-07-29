"""
Form field management functionality for Tallyfy SDK
"""

from typing import List, Optional, Dict, Any
from .models import Capture, Step, Template, TallyfyError


class FormFieldManagement:
    """Handles form field operations"""
    
    def __init__(self, sdk):
        self.sdk = sdk

    def add_form_field_to_step(self, org_id: str, template_id: str, step_id: str, field_data: Dict[str, Any]) -> Optional[Capture]:
        """
        Add form fields (text, dropdown, date, etc.) to a step.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            step_id: Step ID
            field_data: Form field creation data including field_type, label, required, etc.
            
        Returns:
            Created Capture object or None if creation failed
            
        Raises:
            TallyfyError: If the request fails
        """
        try:
            endpoint = f"organizations/{org_id}/checklists/{template_id}/steps/{step_id}/captures"
            
            # Validate required fields
            required_fields = ['field_type', 'label']
            for field in required_fields:
                if field not in field_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Set defaults for optional fields
            capture_data = {
                'field_type': field_data['field_type'],
                'label': field_data['label'],
                'required': field_data.get('required', True),
                'position': field_data.get('position', 1)
            }
            
            # Add optional fields if provided
            optional_fields = ['guidance', 'options', 'default_value', 'default_value_enabled']
            for field in optional_fields:
                if field in field_data:
                    capture_data[field] = field_data[field]
            
            response_data = self.sdk._make_request('POST', endpoint, data=capture_data)
            
            if isinstance(response_data, dict) and 'data' in response_data:
                capture_data = response_data['data']
                return Capture.from_dict(capture_data)
            else:
                self.sdk.logger.warning("Unexpected response format for form field creation")
                return None
                
        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to add form field to step {step_id}: {e}")
            raise

    def update_form_field(self, org_id: str, template_id: str, step_id: str, field_id: str, **kwargs) -> Optional[Capture]:
        """
        Update form field properties, validation, options.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            step_id: Step ID
            field_id: Form field ID
            **kwargs: Form field properties to update
            
        Returns:
            Updated Capture object or None if update failed
            
        Raises:
            TallyfyError: If the request fails
        """
        try:
            endpoint = f"organizations/{org_id}/checklists/{template_id}/steps/{step_id}/captures/{field_id}"
            
            # Build update data from kwargs
            update_data = {}
            allowed_fields = [
                'field_type', 'label', 'guidance', 'position', 'required',
                'options', 'default_value', 'default_value_enabled'
            ]
            
            for field, value in kwargs.items():
                if field in allowed_fields:
                    update_data[field] = value
                else:
                    self.sdk.logger.warning(f"Ignoring unknown form field: {field}")
            
            if not update_data:
                raise ValueError("No valid form field properties provided for update")
            
            response_data = self.sdk._make_request('PUT', endpoint, data=update_data)
            
            if isinstance(response_data, dict) and 'data' in response_data:
                capture_data = response_data['data']
                return Capture.from_dict(capture_data)
            else:
                self.sdk.logger.warning("Unexpected response format for form field update")
                return None
                
        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to update form field {field_id}: {e}")
            raise

    def move_form_field(self, org_id: str, template_id: str, from_step: str, field_id: str, to_step: str, position: int = 1) -> bool:
        """
        Move form field between steps.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            from_step: Source step ID
            field_id: Form field ID to move
            to_step: Target step ID
            position: Position in target step (default: 1)
            
        Returns:
            True if move was successful
            
        Raises:
            TallyfyError: If the request fails
        """
        try:
            endpoint = f"organizations/{org_id}/checklists/{template_id}/steps/{from_step}/captures/{field_id}/move"
            
            move_data = {
                'to_step_id': to_step,
                'position': position
            }
            
            response_data = self.sdk._make_request('POST', endpoint, data=move_data)
            
            # Check if move was successful
            return isinstance(response_data, dict) and response_data.get('success', False)
            
        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to move form field {field_id}: {e}")
            raise

    def delete_form_field(self, org_id: str, template_id: str, step_id: str, field_id: str) -> bool:
        """
        Delete a form field from a step.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            step_id: Step ID
            field_id: Form field ID
            
        Returns:
            True if deletion was successful
            
        Raises:
            TallyfyError: If the request fails
        """
        try:
            endpoint = f"organizations/{org_id}/checklists/{template_id}/steps/{step_id}/captures/{field_id}"
            
            response_data = self.sdk._make_request('DELETE', endpoint)
            
            # Check if deletion was successful
            return isinstance(response_data, dict) and response_data.get('success', False)
            
        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to delete form field {field_id}: {e}")
            raise

    def get_dropdown_options(self, org_id: str, template_id: str, step_id: str, field_id: str) -> List[str]:
        """
        Get current dropdown options for analysis.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            step_id: Step ID
            field_id: Form field ID
            
        Returns:
            List of dropdown option strings
            
        Raises:
            TallyfyError: If the request fails
        """
        try:
            endpoint = f"organizations/{org_id}/checklists/{template_id}/steps/{step_id}/captures/{field_id}"
            
            response_data = self.sdk._make_request('GET', endpoint)
            
            if isinstance(response_data, dict) and 'data' in response_data:
                capture_data = response_data['data']
                options = capture_data.get('options', [])
                
                # Extract option values/labels
                if isinstance(options, list):
                    return [opt.get('label', opt.get('value', str(opt))) if isinstance(opt, dict) else str(opt) for opt in options]
                else:
                    return []
            else:
                self.sdk.logger.warning("Unexpected response format for form field options")
                return []
                
        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to get dropdown options for field {field_id}: {e}")
            raise

    def update_dropdown_options(self, org_id: str, template_id: str, step_id: str, field_id: str, options: List[str]) -> bool:
        """
        Update dropdown options (for external data integration).
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            step_id: Step ID
            field_id: Form field ID
            options: List of new option strings
            
        Returns:
            True if update was successful
            
        Raises:
            TallyfyError: If the request fails
        """
        try:
            # Format options for API
            formatted_options = []
            for i, option in enumerate(options):
                if isinstance(option, str):
                    formatted_options.append({
                        'value': option.lower().replace(' ', '_'),
                        'label': option,
                        'position': i + 1
                    })
                elif isinstance(option, dict):
                    formatted_options.append(option)
                else:
                    formatted_options.append({
                        'value': str(option),
                        'label': str(option),
                        'position': i + 1
                    })
            
            # Update the field with new options
            updated_capture = self.update_form_field(
                org_id, template_id, step_id, field_id,
                options=formatted_options
            )
            
            return updated_capture is not None
                
        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to update dropdown options for field {field_id}: {e}")
            raise

    def suggest_form_fields_for_step(self, org_id: str, template_id: str, step_id: str) -> List[Dict[str, Any]]:
        """
        AI-powered suggestions for relevant form fields based on step content.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            step_id: Step ID to analyze
            
        Returns:
            List of suggested form field configurations
            
        Raises:
            TallyfyError: If the request fails
        """
        try:
            # Get the step details to analyze
            step = self.get_step(org_id, template_id, step_id)
            if not step:
                raise TallyfyError(f"Step {step_id} not found")
            
            # Get template context for better suggestions
            template = self.sdk.get_template(org_id, template_id)
            if not template:
                raise TallyfyError(f"Template {template_id} not found")
            
            # Analyze step content for intelligent suggestions
            step_title = step.title.lower() if step.title else ''
            step_summary = step.summary.lower() if step.summary else ''
            step_type = step.step_type or 'task'
            existing_fields = step.captures or []
            
            # Combined text for analysis
            step_text = f"{step_title} {step_summary}".strip()
            
            suggestions = []
            
            # Rule-based suggestions based on common patterns
            field_patterns = {
                # Approval and Review patterns
                'approval': {
                    'keywords': ['approve', 'review', 'sign off', 'accept', 'reject', 'confirm'],
                    'fields': [
                        {
                            'field_type': 'dropdown',
                            'label': 'Decision',
                            'options': [{'value': 'approved', 'label': 'Approved'}, {'value': 'rejected', 'label': 'Rejected'}, {'value': 'needs_revision', 'label': 'Needs Revision'}],
                            'required': True,
                            'reasoning': 'Approval steps typically need a decision field'
                        },
                        {
                            'field_type': 'textarea',
                            'label': 'Comments',
                            'required': False,
                            'reasoning': 'Comments are useful for providing feedback'
                        }
                    ]
                },
                
                # Contact and Communication patterns
                'contact': {
                    'keywords': ['contact', 'call', 'email', 'phone', 'reach out', 'communicate'],
                    'fields': [
                        {
                            'field_type': 'text',
                            'label': 'Contact Method',
                            'required': True,
                            'reasoning': 'Track how contact was made'
                        },
                        {
                            'field_type': 'date',
                            'label': 'Contact Date',
                            'required': True,
                            'reasoning': 'Record when contact was made'
                        },
                        {
                            'field_type': 'textarea',
                            'label': 'Contact Notes',
                            'required': False,
                            'reasoning': 'Document the conversation or interaction'
                        }
                    ]
                },
                
                # Document and File patterns
                'document': {
                    'keywords': ['document', 'file', 'upload', 'attach', 'report', 'contract', 'agreement'],
                    'fields': [
                        {
                            'field_type': 'file',
                            'label': 'Document Upload',
                            'required': True,
                            'reasoning': 'File upload for document-related steps'
                        },
                        {
                            'field_type': 'text',
                            'label': 'Document Title',
                            'required': False,
                            'reasoning': 'Name or title of the document'
                        },
                        {
                            'field_type': 'textarea',
                            'label': 'Document Description',
                            'required': False,
                            'reasoning': 'Brief description of the document'
                        }
                    ]
                },
                
                # Payment and Financial patterns
                'payment': {
                    'keywords': ['payment', 'invoice', 'cost', 'price', 'amount', 'bill', 'expense'],
                    'fields': [
                        {
                            'field_type': 'number',
                            'label': 'Amount',
                            'required': True,
                            'reasoning': 'Financial steps need amount tracking'
                        },
                        {
                            'field_type': 'dropdown',
                            'label': 'Currency',
                            'options': [{'value': 'USD', 'label': 'USD'}, {'value': 'EUR', 'label': 'EUR'}, {'value': 'GBP', 'label': 'GBP'}],
                            'required': True,
                            'reasoning': 'Specify currency for financial transactions'
                        },
                        {
                            'field_type': 'date',
                            'label': 'Payment Date',
                            'required': False,
                            'reasoning': 'Track when payment was made'
                        }
                    ]
                },
                
                # Quality and Testing patterns
                'quality': {
                    'keywords': ['test', 'quality', 'check', 'verify', 'validate', 'inspect'],
                    'fields': [
                        {
                            'field_type': 'dropdown',
                            'label': 'Test Result',
                            'options': [{'value': 'pass', 'label': 'Pass'}, {'value': 'fail', 'label': 'Fail'}, {'value': 'partial', 'label': 'Partial Pass'}],
                            'required': True,
                            'reasoning': 'Quality steps need result tracking'
                        },
                        {
                            'field_type': 'textarea',
                            'label': 'Test Notes',
                            'required': False,
                            'reasoning': 'Document test findings and issues'
                        },
                        {
                            'field_type': 'number',
                            'label': 'Score',
                            'required': False,
                            'reasoning': 'Numerical rating for quality assessment'
                        }
                    ]
                },
                
                # Schedule and Time patterns
                'schedule': {
                    'keywords': ['schedule', 'meeting', 'appointment', 'deadline', 'due', 'time'],
                    'fields': [
                        {
                            'field_type': 'datetime',
                            'label': 'Scheduled Time',
                            'required': True,
                            'reasoning': 'Scheduling steps need date and time'
                        },
                        {
                            'field_type': 'text',
                            'label': 'Location',
                            'required': False,
                            'reasoning': 'Meeting location or venue'
                        },
                        {
                            'field_type': 'textarea',
                            'label': 'Agenda',
                            'required': False,
                            'reasoning': 'Meeting agenda or notes'
                        }
                    ]
                }
            }
            
            # Check existing field types to avoid duplicates
            existing_field_types = set()
            existing_field_labels = set()
            for field in existing_fields:
                if hasattr(field, 'field_type'):
                    existing_field_types.add(field.field_type)
                if hasattr(field, 'label'):
                    existing_field_labels.add(field.label.lower())
            
            # Analyze step content against patterns
            matched_patterns = []
            for pattern_name, pattern_data in field_patterns.items():
                keyword_matches = sum(1 for keyword in pattern_data['keywords'] if keyword in step_text)
                if keyword_matches > 0:
                    matched_patterns.append((pattern_name, keyword_matches, pattern_data))
            
            # Sort by relevance (number of keyword matches)
            matched_patterns.sort(key=lambda x: x[1], reverse=True)
            
            # Generate suggestions from matched patterns
            suggested_count = 0
            max_suggestions = 5
            
            for pattern_name, matches, pattern_data in matched_patterns:
                if suggested_count >= max_suggestions:
                    break
                    
                for field_config in pattern_data['fields']:
                    if suggested_count >= max_suggestions:
                        break
                    
                    # Skip if similar field already exists
                    field_label_lower = field_config['label'].lower()
                    if field_label_lower in existing_field_labels:
                        continue
                    
                    # Add suggestion with metadata
                    suggestion = {
                        'field_config': field_config.copy(),
                        'confidence': min(0.9, 0.3 + (matches * 0.2)),  # Confidence based on keyword matches
                        'pattern_matched': pattern_name,
                        'keyword_matches': matches,
                        'priority': 'high' if matches >= 2 else 'medium' if matches >= 1 else 'low'
                    }
                    
                    # Add position suggestion
                    suggestion['field_config']['position'] = len(existing_fields) + suggested_count + 1
                    
                    suggestions.append(suggestion)
                    suggested_count += 1
            
            # If no specific patterns matched, provide generic useful fields
            if not suggestions:
                generic_suggestions = [
                    {
                        'field_config': {
                            'field_type': 'textarea',
                            'label': 'Notes',
                            'required': False,
                            'position': len(existing_fields) + 1
                        },
                        'confidence': 0.6,
                        'pattern_matched': 'generic',
                        'keyword_matches': 0,
                        'priority': 'medium',
                        'reasoning': 'Notes field is useful for most steps to capture additional information'
                    },
                    {
                        'field_config': {
                            'field_type': 'dropdown',
                            'label': 'Status',
                            'options': [{'value': 'completed', 'label': 'Completed'}, {'value': 'in_progress', 'label': 'In Progress'}, {'value': 'blocked', 'label': 'Blocked'}],
                            'required': False,
                            'position': len(existing_fields) + 2
                        },
                        'confidence': 0.5,
                        'pattern_matched': 'generic',
                        'keyword_matches': 0,
                        'priority': 'low',
                        'reasoning': 'Status tracking can be helpful for workflow management'
                    }
                ]
                suggestions = generic_suggestions
            
            # Add implementation guidance
            for suggestion in suggestions:
                suggestion['implementation'] = {
                    'method': 'add_form_field_to_step',
                    'parameters': {
                        'org_id': org_id,
                        'template_id': template_id,
                        'step_id': step_id,
                        'field_data': suggestion['field_config']
                    }
                }
            
            return suggestions
            
        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to suggest form fields for step {step_id}: {e}")
            raise

    def get_step(self, org_id: str, template_id: str, step_id: str) -> Optional[Step]:
        """
        Get a specific step with its details.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            step_id: Step ID
            
        Returns:
            Step object or None if not found
            
        Raises:
            TallyfyError: If the request fails
        """
        try:
            endpoint = f"organizations/{org_id}/checklists/{template_id}/steps/{step_id}"
            response_data = self.sdk._make_request('GET', endpoint)
            
            if isinstance(response_data, dict) and 'data' in response_data:
                step_data = response_data['data']
                return Step.from_dict(step_data)
            else:
                self.sdk.logger.warning("Unexpected response format for step")
                return None
                
        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to get step {step_id}: {e}")
            raise