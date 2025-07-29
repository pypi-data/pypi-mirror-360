"""
Template management functionality for Tallyfy SDK
"""

from typing import List, Optional, Dict, Any
from .models import Template, Step, AutomatedAction, PrerunField, TallyfyError, TemplatesList


class TemplateManagement:
    """Handles template and step management operations"""
    
    def __init__(self, sdk):
        self.sdk = sdk

    def search_templates_by_name(self, org_id: str, template_name: str) -> str:
        """
        Search for template by name using the search endpoint.

        Args:
            org_id: Organization ID
            template_name: Name or partial name of the template to search for

        Returns:
            Template ID of the found template

        Raises:
            TallyfyError: If no template found, multiple matches, or search fails
        """
        try:
            search_endpoint = f"organizations/{org_id}/search"
            search_params = {
                'on': 'blueprint',
                'per_page': '20',
                'search': template_name
            }

            search_response = self.sdk._make_request('GET', search_endpoint, params=search_params)

            if isinstance(search_response, dict) and 'blueprint' in search_response:
                template_data = search_response['blueprint']
                if 'data' in template_data and template_data['data']:
                    templates = template_data['data']

                    # First try exact match (case-insensitive)
                    exact_matches = [p for p in templates if p['title'].lower() == template_name.lower()]
                    if exact_matches:
                        return exact_matches[0]['id']
                    elif len(templates) == 1:
                        # Single search result, use it
                        return templates[0]['id']
                    else:
                        # Multiple matches found, provide helpful error with options
                        match_names = [f"'{p['title']}'" for p in templates[:5]]  # Show max 5
                        raise TallyfyError(
                            f"Multiple templates found matching '{template_name}': {', '.join(match_names)}. Please be more specific.")
                else:
                    raise TallyfyError(f"No template found matching name: {template_name}")
            else:
                raise TallyfyError(f"Search failed for template name: {template_name}")

        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to search for template '{template_name}': {e}")
            raise

    def get_template(self, org_id: str, template_id: Optional[str] = None, template_name: Optional[str] = None) -> Optional[Template]:
        """
        Get a template (checklist) by its ID or name with full details including prerun fields,
        automated actions, linked tasks, and metadata.

        Args:
            org_id: Organization ID
            template_id: Template (checklist) ID
            template_name: Template (checklist) name

        Returns:
            Template object with complete template data

        Raises:
            TallyfyError: If the request fails
        """
        if not template_id and not template_name:
            raise ValueError("Either template_id or template_name must be provided")

        try:
            # If template_name is provided but not template_id, search for the template first
            if template_name and not template_id:
                template_id = self.search_templates_by_name(org_id, template_name)
            
            endpoint = f"organizations/{org_id}/checklists/{template_id}"
            response_data = self.sdk._make_request('GET', endpoint)

            if isinstance(response_data, dict) and 'data' in response_data:
                template_data = response_data['data']
                return Template.from_dict(template_data)
            else:
                self.sdk.logger.warning("Unexpected response format for template")
                return None

        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to get template {template_id} for org {org_id}: {e}")
            raise

    def get_all_templates(self, org_id: str) -> TemplatesList:
        """
        Get all templates (checklists) for an organization with pagination metadata.

        Args:
            org_id: Organization ID

        Returns:
            TemplatesList object containing list of templates and pagination metadata

        Raises:
            TallyfyError: If the request fails
        """
        try:
            endpoint = f"organizations/{org_id}/checklists"
            response_data = self.sdk._make_request('GET', endpoint)

            if isinstance(response_data, dict):
                return TemplatesList.from_dict(response_data)
            else:
                self.sdk.logger.warning("Unexpected response format for templates list")
                return TemplatesList(data=[], meta=None)

        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to get all templates for org {org_id}: {e}")
            raise

    def update_template_metadata(self, org_id: str, template_id: str, **kwargs) -> Optional[Template]:
        """
        Update template metadata like title, summary, guidance, icons, etc.
        
        Args:
            org_id: Organization ID
            template_id: Template ID to update
            **kwargs: Template metadata fields to update (title, summary, guidance, icon, etc.)
        
        Returns:
            Updated Template object
            
        Raises:
            TallyfyError: If the request fails
        """
        try:
            endpoint = f"organizations/{org_id}/checklists/{template_id}"
            
            # Build update data from kwargs
            update_data = {}
            allowed_fields = [
                'title', 'summary', 'guidance', 'icon', 'alias', 'webhook',
                'explanation_video', 'kickoff_title', 'kickoff_description',
                'is_public', 'is_featured', 'auto_naming', 'folderize_process',
                'tag_process', 'allow_launcher_change_name', 'is_pinned',
                'default_folder', 'folder_changeable_by_launcher'
            ]
            
            for field, value in kwargs.items():
                if field in allowed_fields:
                    update_data[field] = value
                else:
                    self.sdk.logger.warning(f"Ignoring unknown template field: {field}")
            
            if not update_data:
                raise ValueError("No valid template fields provided for update")
            
            response_data = self.sdk._make_request('PUT', endpoint, data=update_data)
            
            if isinstance(response_data, dict) and 'data' in response_data:
                template_data = response_data['data']
                return Template.from_dict(template_data)
            else:
                self.sdk.logger.warning("Unexpected response format for template update")
                return None
                
        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to update template {template_id} for org {org_id}: {e}")
            raise

    def get_template_with_steps(self, org_id: str, template_id: Optional[str] = None, template_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get template with full step details and structure.
        
        Args:
            org_id: Organization ID
            template_id: Template ID to retrieve
            template_name: Template name to retrieve (alternative to template_id)
        
        Returns:
            Dictionary containing template data with full step details
            
        Raises:
            TallyfyError: If the request fails
        """
        if not template_id and not template_name:
            raise ValueError("Either template_id or template_name must be provided")
        
        try:
            # If template_name is provided but not template_id, search for the template first
            if template_name and not template_id:
                template_id = self.search_templates_by_name(org_id, template_name)
            
            # Get template with steps included
            endpoint = f"organizations/{org_id}/checklists/{template_id}"
            params = {'with': 'steps,automated_actions,prerun'}
            
            response_data = self.sdk._make_request('GET', endpoint, params=params)
            
            if isinstance(response_data, dict) and 'data' in response_data:
                template_data = response_data['data']
                
                return {
                    'template': Template.from_dict(template_data),
                    'raw_data': template_data,
                    'step_count': len(template_data.get('steps', [])),
                    'steps': template_data.get('steps', []),
                    'automation_count': len(template_data.get('automated_actions', [])),
                    'prerun_field_count': len(template_data.get('prerun', []))
                }
            else:
                self.sdk.logger.warning("Unexpected response format for template with steps")
                return None
                
        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to get template with steps {template_id or template_name} for org {org_id}: {e}")
            raise

    def duplicate_template(self, org_id: str, template_id: str, new_name: str, copy_permissions: bool = False) -> Optional[Template]:
        """
        Create a copy of a template for safe editing.
        
        Args:
            org_id: Organization ID
            template_id: Template ID to duplicate
            new_name: Name for the new template copy
            copy_permissions: Whether to copy template permissions (default: False)
        
        Returns:
            New Template object
            
        Raises:
            TallyfyError: If the request fails
        """
        try:
            endpoint = f"organizations/{org_id}/checklists/{template_id}/duplicate"
            
            duplicate_data = {
                'title': new_name,
                'copy_permissions': copy_permissions
            }
            
            response_data = self.sdk._make_request('POST', endpoint, data=duplicate_data)
            
            if isinstance(response_data, dict) and 'data' in response_data:
                template_data = response_data['data']
                return Template.from_dict(template_data)
            else:
                self.sdk.logger.warning("Unexpected response format for template duplication")
                return None
                
        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to duplicate template {template_id} for org {org_id}: {e}")
            raise

    def get_template_steps(self, org_id: str, template_id: str) -> List[Step]:
        """
        Get all steps of a template.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
        
        Returns:
            List of Step objects
            
        Raises:
            TallyfyError: If the request fails
        """
        try:
            endpoint = f"organizations/{org_id}/checklists/{template_id}/steps"
            response_data = self.sdk._make_request('GET', endpoint)
            
            if isinstance(response_data, dict) and 'data' in response_data:
                steps_data = response_data['data']
                return [Step.from_dict(step_data) for step_data in steps_data]
            else:
                if isinstance(response_data, list):
                    return [Step.from_dict(step_data) for step_data in response_data]
                else:
                    self.sdk.logger.warning("Unexpected response format for template steps")
                    return []
                    
        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to get template steps for template {template_id}: {e}")
            raise

    def get_step_dependencies(self, org_id: str, template_id: str, step_id: str) -> Dict[str, Any]:
        """
        Analyze which automations affect when this step appears.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            step_id: Step ID to analyze
            
        Returns:
            Dictionary containing dependency analysis with:
            - step_info: Basic step information
            - automation_rules: List of automations that affect this step
            - dependencies: List of conditions that must be met for step to show
            - affected_by: List of other steps/fields that influence this step's visibility
        """
        try:
            # Get template with automations
            template_data = self.get_template_with_steps(org_id, template_id)
            if not template_data:
                raise TallyfyError(f"Could not retrieve template {template_id}")
            
            # Find the target step
            target_step = None
            for step_data in template_data['steps']:
                if step_data.get('id') == step_id:
                    target_step = step_data
                    break
            
            if not target_step:
                raise TallyfyError(f"Step {step_id} not found in template {template_id}")
            
            # Analyze automation rules that affect this step
            automation_rules = []
            dependencies = []
            affected_by = []
            
            template = template_data['template']
            if hasattr(template, 'automated_actions') and template.automated_actions:
                for automation in template.automated_actions:
                    # Check if this automation affects our target step
                    step_affected = False
                    for action in automation.then_actions:
                        if (action.target_step_id == step_id or 
                            action.actionable_id == step_id):
                            step_affected = True
                            break
                    
                    if step_affected:
                        automation_rules.append({
                            'automation_id': automation.id,
                            'alias': automation.automated_alias,
                            'conditions': [
                                {
                                    'id': cond.id,
                                    'type': cond.conditionable_type,
                                    'target_id': cond.conditionable_id,
                                    'operation': cond.operation,
                                    'statement': cond.statement,
                                    'logic': cond.logic
                                } for cond in automation.conditions
                            ],
                            'actions': [
                                {
                                    'id': action.id,
                                    'type': action.action_type,
                                    'verb': action.action_verb,
                                    'target_step_id': action.target_step_id
                                } for action in automation.then_actions
                            ]
                        })
                        
                        # Extract dependencies from conditions
                        for condition in automation.conditions:
                            if condition.conditionable_type in ['Step', 'Capture']:
                                dependencies.append({
                                    'type': condition.conditionable_type.lower(),
                                    'id': condition.conditionable_id,
                                    'requirement': f"{condition.operation} {condition.statement}",
                                    'logic': condition.logic
                                })
                                
                                affected_by.append({
                                    'type': condition.conditionable_type.lower(),
                                    'id': condition.conditionable_id,
                                    'influence': f"Step visibility depends on this {condition.conditionable_type.lower()}"
                                })
            
            return {
                'step_info': {
                    'id': target_step.get('id'),
                    'title': target_step.get('title'),
                    'position': target_step.get('position'),
                    'step_type': target_step.get('step_type')
                },
                'automation_rules': automation_rules,
                'dependencies': dependencies,
                'affected_by': affected_by,
                'dependency_count': len(dependencies),
                'has_conditional_visibility': len(automation_rules) > 0
            }
            
        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to analyze step dependencies for step {step_id}: {e}")
            raise

    def suggest_step_deadline(self, org_id: str, template_id: str, step_id: str) -> Dict[str, Any]:
        """
        Suggest reasonable deadline based on step type and complexity.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            step_id: Step ID to analyze
            
        Returns:
            Dictionary containing deadline suggestions with:
            - step_info: Basic step information
            - suggested_deadline: Recommended deadline configuration
            - reasoning: Explanation for the suggestion
            - alternatives: Other deadline options
        """
        try:
            # Get template and step details
            template_data = self.get_template_with_steps(org_id, template_id)
            if not template_data:
                raise TallyfyError(f"Could not retrieve template {template_id}")
            
            # Find the target step
            target_step = None
            for step_data in template_data['steps']:
                if step_data.get('id') == step_id:
                    target_step = step_data
                    break
            
            if not target_step:
                raise TallyfyError(f"Step {step_id} not found in template {template_id}")
            
            # Analyze step characteristics
            step_title = target_step.get('title', '').lower()
            step_summary = target_step.get('summary', '').lower()
            step_type = target_step.get('step_type', '')
            captures = target_step.get('captures', [])
            
            # Default suggestion
            suggested_deadline = {
                'value': 2,
                'unit': 'business_days',
                'option': 'from',
                'step': 'start_run'
            }
            
            reasoning = "Standard deadline for typical workflow steps"
            alternatives = []
            
            # Adjust based on step characteristics
            content = f"{step_title} {step_summary}"
            
            # Quick tasks (1 business day)
            if any(word in content for word in ['approve', 'review', 'check', 'verify', 'confirm', 'acknowledge']):
                suggested_deadline.update({'value': 1, 'unit': 'business_days'})
                reasoning = "Quick approval/review tasks typically need fast turnaround"
                alternatives = [
                    {'value': 2, 'unit': 'business_days', 'description': 'Standard timeline'},
                    {'value': 4, 'unit': 'hours', 'description': 'Urgent approval'},
                ]
            
            # Complex tasks (1 week)
            elif any(word in content for word in ['develop', 'create', 'design', 'write', 'prepare', 'plan', 'analyze']):
                suggested_deadline.update({'value': 1, 'unit': 'weeks'})
                reasoning = "Creative/development work requires adequate time for quality output"
                alternatives = [
                    {'value': 3, 'unit': 'business_days', 'description': 'Accelerated timeline'},
                    {'value': 2, 'unit': 'weeks', 'description': 'Extended timeline for complex work'},
                ]
            
            # External coordination (3-5 days)
            elif any(word in content for word in ['coordinate', 'schedule', 'contact', 'notify', 'communicate']):
                suggested_deadline.update({'value': 3, 'unit': 'business_days'})
                reasoning = "External coordination requires time for responses and scheduling"
                alternatives = [
                    {'value': 1, 'unit': 'business_days', 'description': 'Internal coordination only'},
                    {'value': 1, 'unit': 'weeks', 'description': 'Complex external coordination'},
                ]
            
            # Legal/compliance (2 weeks)
            elif any(word in content for word in ['legal', 'compliance', 'audit', 'regulation', 'contract']):
                suggested_deadline.update({'value': 2, 'unit': 'weeks'})
                reasoning = "Legal and compliance work requires thorough review and documentation"
                alternatives = [
                    {'value': 1, 'unit': 'weeks', 'description': 'Simple legal review'},
                    {'value': 1, 'unit': 'months', 'description': 'Complex legal/regulatory work'},
                ]
            
            # Adjust based on form complexity
            if captures:
                complex_fields = len([c for c in captures if c.get('field_type') in ['file', 'wysiwyg', 'table']])
                if complex_fields > 2:
                    # Add extra time for complex forms
                    if suggested_deadline['unit'] == 'business_days':
                        suggested_deadline['value'] += 1
                    reasoning += " (adjusted for complex form fields)"
            
            return {
                'step_info': {
                    'id': target_step.get('id'),
                    'title': target_step.get('title'),
                    'step_type': step_type,
                    'form_field_count': len(captures),
                    'position': target_step.get('position')
                },
                'suggested_deadline': suggested_deadline,
                'reasoning': reasoning,
                'alternatives': alternatives,
                'confidence': 'medium',  # Could be calculated based on keyword matches
                'factors_considered': [
                    'Step title keywords',
                    'Step summary content', 
                    'Form field complexity',
                    'Step type classification'
                ]
            }
            
        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to suggest deadline for step {step_id}: {e}")
            raise

    def create_automation_rule(self, org_id: str, template_id: str, automation_data: Dict[str, Any]) -> AutomatedAction:
        """
        Create conditional automation (if-then rules).
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            automation_data: Dictionary containing automation rule data with conditions and actions
        
        Returns:
            AutomatedAction object
            
        Raises:
            TallyfyError: If the request fails
        """
        try:
            endpoint = f"organizations/{org_id}/checklists/{template_id}/automated_actions"
            response_data = self.sdk._make_request('POST', endpoint, data=automation_data)
            
            if isinstance(response_data, dict) and 'data' in response_data:
                automation_data = response_data['data']
                return AutomatedAction.from_dict(automation_data)
            else:
                self.sdk.logger.warning("Unexpected response format for automation creation")
                return None
                
        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to create automation rule for template {template_id}: {e}")
            raise

    def update_automation_rule(self, org_id: str, template_id: str, automation_id: str, **kwargs) -> AutomatedAction:
        """
        Modify automation conditions and actions.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            automation_id: Automation rule ID
            **kwargs: Automation fields to update
        
        Returns:
            Updated AutomatedAction object
            
        Raises:
            TallyfyError: If the request fails
        """
        try:
            endpoint = f"organizations/{org_id}/checklists/{template_id}/automated_actions/{automation_id}"
            
            # Build update data from kwargs
            update_data = {}
            allowed_fields = [
                'automated_alias', 'conditions', 'then_actions'
            ]
            
            for field, value in kwargs.items():
                if field in allowed_fields:
                    update_data[field] = value
                else:
                    self.sdk.logger.warning(f"Ignoring unknown automation field: {field}")
            
            if not update_data:
                raise ValueError("No valid automation fields provided for update")
            
            response_data = self.sdk._make_request('PUT', endpoint, data=update_data)
            
            if isinstance(response_data, dict) and 'data' in response_data:
                automation_data = response_data['data']
                return AutomatedAction.from_dict(automation_data)
            else:
                self.sdk.logger.warning("Unexpected response format for automation update")
                return None
                
        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to update automation rule {automation_id}: {e}")
            raise

    def delete_automation_rule(self, org_id: str, template_id: str, automation_id: str) -> bool:
        """
        Remove an automation rule.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            automation_id: Automation rule ID
        
        Returns:
            True if deletion was successful
            
        Raises:
            TallyfyError: If the request fails
        """
        try:
            endpoint = f"organizations/{org_id}/checklists/{template_id}/automated_actions/{automation_id}"
            response_data = self.sdk._make_request('DELETE', endpoint)
            
            return True
            
        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to delete automation rule {automation_id}: {e}")
            raise

    def analyze_template_automations(self, org_id: str, template_id: str) -> Dict[str, Any]:
        """
        Analyze all automations for conflicts, redundancies, and optimization opportunities.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
        
        Returns:
            Dictionary containing automation analysis with:
            - total_automations: Count of automation rules
            - conflicts: List of conflicting rules
            - redundancies: List of redundant rules
            - optimization_opportunities: Suggested improvements
            - complexity_score: Overall complexity rating
        """
        try:
            template_data = self.get_template_with_steps(org_id, template_id)
            if not template_data:
                raise TallyfyError(f"Could not retrieve template {template_id}")
            template = template_data['template']
            automations = template.automated_actions or []
            conflicts = []
            redundancies = []
            optimization_opportunities = []
            
            # Analyze conflicts and redundancies
            for i, automation1 in enumerate(automations):
                for j, automation2 in enumerate(automations[i+1:], i+1):
                    # Check for conflicting actions on same targets
                    targets1 = set()
                    targets2 = set()

                    for action in automation1.then_actions:
                        if hasattr(action, 'target_step_id') and action.target_step_id:
                            targets1.add(action.target_step_id)
                        if hasattr(action, 'actionable_id') and action.actionable_id:
                            targets1.add(action.actionable_id)

                    for action in automation2.then_actions:
                        if hasattr(action, 'target_step_id') and action.target_step_id:
                            targets2.add(action.target_step_id)
                        if hasattr(action, 'actionable_id') and action.actionable_id:
                            targets2.add(action.actionable_id)

                    common_targets = targets1.intersection(targets2)
                    if common_targets:
                        # Check if conditions could trigger simultaneously
                        similar_conditions = self._analyze_condition_similarity(automation1.conditions, automation2.conditions)

                        if similar_conditions['similarity_score'] > 0.7:
                            conflicts.append({
                                'automation1_id': automation1.id,
                                'automation1_alias': automation1.automated_alias,
                                'automation2_id': automation2.id,
                                'automation2_alias': automation2.automated_alias,
                                'common_targets': list(common_targets),
                                'conflict_type': 'overlapping_conditions',
                                'similarity_score': similar_conditions['similarity_score'],
                                'risk_level': 'high' if similar_conditions['similarity_score'] > 0.9 else 'medium'
                            })

                        # Check for exact condition duplicates (redundancies)
                        if similar_conditions['similarity_score'] == 1.0:
                            redundancies.append({
                                'automation1_id': automation1.id,
                                'automation2_id': automation2.id,
                                'redundancy_type': 'identical_conditions',
                                'recommendation': 'Consider consolidating these rules'
                            })
            
            # Identify optimization opportunities
            
            # 1. Single-condition automations that could be merged
            single_condition_automations = [a for a in automations if len(a.conditions) == 1]
            if len(single_condition_automations) > 3:
                optimization_opportunities.append({
                    'type': 'merge_simple_rules',
                    'description': f"Found {len(single_condition_automations)} single-condition rules that could potentially be consolidated",
                    'impact': 'medium',
                    'automation_ids': [a.id for a in single_condition_automations]
                })
            
            # 2. Unused or ineffective automations
            steps = template_data.get('steps', [])
            if len(steps) > 0:
                steps = steps['data']
                step_ids = set(step['id'] for step in steps)
                for automation in automations:
                    has_valid_targets = False
                    for action in automation.then_actions:
                        target_id = getattr(action, 'target_step_id', None) or getattr(action, 'actionable_id', None)
                        if target_id and target_id in step_ids:
                            has_valid_targets = True
                            break

                    if not has_valid_targets:
                        optimization_opportunities.append({
                            'type': 'orphaned_automation',
                            'description': f"Automation '{automation.automated_alias}' targets non-existent steps",
                            'impact': 'high',
                            'automation_id': automation.id,
                            'recommendation': 'Review and update target steps or remove this automation'
                        })
            
            # 3. Overly complex condition chains
            for automation in automations:
                if len(automation.conditions) > 5:
                    optimization_opportunities.append({
                        'type': 'complex_conditions',
                        'description': f"Automation '{automation.automated_alias}' has {len(automation.conditions)} conditions",
                        'impact': 'medium',
                        'automation_id': automation.id,
                        'recommendation': 'Consider breaking into simpler rules for better maintainability'
                    })
            
            # Calculate complexity score
            complexity_factors = {
                'total_automations': len(automations),
                'total_conditions': sum(len(a.conditions) for a in automations),
                'total_actions': sum(len(a.then_actions) for a in automations),
                'conflicts': len(conflicts),
                'redundancies': len(redundancies)
            }
            
            complexity_score = min(100, (
                complexity_factors['total_automations'] * 5 +
                complexity_factors['total_conditions'] * 2 +
                complexity_factors['total_actions'] * 2 +
                complexity_factors['conflicts'] * 15 +
                complexity_factors['redundancies'] * 10
            ))
            
            return {
                'total_automations': len(automations),
                'conflicts': conflicts,
                'redundancies': redundancies,
                'optimization_opportunities': optimization_opportunities,
                'complexity_score': complexity_score,
                'complexity_rating': (
                    'low' if complexity_score < 30 else
                    'medium' if complexity_score < 70 else
                    'high'
                ),
                'analysis_summary': {
                    'conflict_count': len(conflicts),
                    'redundancy_count': len(redundancies),
                    'optimization_count': len(optimization_opportunities),
                    'health_status': 'good' if not conflicts and not redundancies else 'needs_attention'
                }
            }
            
        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to analyze template automations for template {template_id}: {e}")
            raise

    def consolidate_automation_rules(self, org_id: str, template_id: str, preview: bool = True) -> Dict[str, Any]:
        """
        Suggest and optionally implement automation consolidation.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            preview: If True, only suggest changes without implementing (default: True)
        
        Returns:
            Dictionary containing consolidation suggestions and results
        """
        try:
            analysis = self.analyze_template_automations(org_id, template_id)
            
            consolidation_plan = []
            savings_estimate = {
                'rules_reduced': 0,
                'conditions_simplified': 0,
                'maintenance_improvement': 0
            }
            
            # Process redundancies
            for redundancy in analysis['redundancies']:
                consolidation_plan.append({
                    'type': 'merge_redundant',
                    'automation_ids': [redundancy['automation1_id'], redundancy['automation2_id']],
                    'action': 'merge_into_single_rule',
                    'benefit': 'Eliminates duplicate logic',
                    'implementation': 'automated' if not preview else 'preview_only'
                })
                savings_estimate['rules_reduced'] += 1
            
            # Process optimization opportunities
            for opportunity in analysis['optimization_opportunities']:
                if opportunity['type'] == 'merge_simple_rules':
                    consolidation_plan.append({
                        'type': 'group_simple_rules',
                        'automation_ids': opportunity['automation_ids'],
                        'action': 'create_multi_condition_rule',
                        'benefit': 'Reduces rule count while maintaining functionality',
                        'implementation': 'manual_review_required'
                    })
                    savings_estimate['rules_reduced'] += len(opportunity['automation_ids']) - 1
                
                elif opportunity['type'] == 'orphaned_automation':
                    consolidation_plan.append({
                        'type': 'remove_orphaned',
                        'automation_ids': [opportunity['automation_id']],
                        'action': 'remove_unused_automation',
                        'benefit': 'Eliminates dead code',
                        'implementation': 'automated' if not preview else 'preview_only'
                    })
                    savings_estimate['rules_reduced'] += 1
            
            # If not preview mode, implement automatic consolidations
            implemented_changes = []
            if not preview:
                for plan_item in consolidation_plan:
                    if plan_item['implementation'] == 'automated':
                        try:
                            if plan_item['type'] == 'remove_orphaned':
                                for automation_id in plan_item['automation_ids']:
                                    self.delete_automation_rule(org_id, template_id, automation_id)
                                    implemented_changes.append({
                                        'action': 'deleted_automation',
                                        'automation_id': automation_id,
                                        'status': 'success'
                                    })
                        except Exception as e:
                            implemented_changes.append({
                                'action': 'failed_automation_deletion',
                                'automation_id': automation_id,
                                'status': 'error',
                                'error': str(e)
                            })
            
            return {
                'preview_mode': preview,
                'consolidation_plan': consolidation_plan,
                'savings_estimate': savings_estimate,
                'implemented_changes': implemented_changes,
                'summary': {
                    'total_suggestions': len(consolidation_plan),
                    'estimated_rule_reduction': savings_estimate['rules_reduced'],
                    'complexity_improvement': min(30, savings_estimate['rules_reduced'] * 5),
                    'requires_manual_review': len([p for p in consolidation_plan if 'manual' in p['implementation']])
                },
                'next_steps': [
                    'Review manual consolidation suggestions',
                    'Test consolidated rules in staging environment',
                    'Monitor automation performance after changes'
                ] if not preview else [
                    'Run with preview=False to implement automatic consolidations',
                    'Review manual suggestions and implement carefully',
                    'Re-analyze after changes to measure improvement'
                ]
            }
            
        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to consolidate automation rules for template {template_id}: {e}")
            raise

    def get_step_visibility_conditions(self, org_id: str, template_id: str, step_id: str) -> Dict[str, Any]:
        """
        Analyze when/how a step becomes visible based on all automations.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            step_id: Step ID to analyze
        
        Returns:
            Dictionary containing step visibility analysis
        """
        try:
            template_data = self.get_template_with_steps(org_id, template_id)
            if not template_data:
                raise TallyfyError(f"Could not retrieve template {template_id}")
            
            # Find the target step
            target_step = None
            for step_data in template_data['steps']:
                if step_data.get('id') == step_id:
                    target_step = step_data
                    break
            
            if not target_step:
                raise TallyfyError(f"Step {step_id} not found in template {template_id}")
            
            visibility_rules = []
            always_visible = True
            visibility_logic = []
            
            template = template_data['template']
            if hasattr(template, 'automated_actions') and template.automated_actions:
                for automation in template.automated_actions:
                    affects_visibility = False
                    show_actions = []
                    hide_actions = []
                    
                    for action in automation.then_actions:
                        if (hasattr(action, 'target_step_id') and action.target_step_id == step_id and
                            hasattr(action, 'action_verb')):
                            if action.action_verb in ['show', 'reveal', 'display']:
                                affects_visibility = True
                                show_actions.append(action)
                                always_visible = False
                            elif action.action_verb in ['hide', 'conceal', 'skip']:
                                affects_visibility = True
                                hide_actions.append(action)
                    
                    if affects_visibility:
                        condition_summary = self._summarize_conditions(automation.conditions)
                        
                        visibility_rules.append({
                            'automation_id': automation.id,
                            'automation_alias': automation.automated_alias,
                            'condition_summary': condition_summary,
                            'show_actions': len(show_actions),
                            'hide_actions': len(hide_actions),
                            'net_effect': 'show' if len(show_actions) > len(hide_actions) else 'hide',
                            'conditions': [
                                {
                                    'type': cond.conditionable_type,
                                    'target': cond.conditionable_id,
                                    'operation': cond.operation,
                                    'value': cond.statement,
                                    'logic': cond.logic
                                } for cond in automation.conditions
                            ]
                        })
                        
                        visibility_logic.append({
                            'rule': f"IF {condition_summary} THEN {show_actions[0].action_verb if show_actions else hide_actions[0].action_verb} step",
                            'effect': 'show' if show_actions else 'hide'
                        })
            
            # Determine overall visibility behavior
            show_rules = [r for r in visibility_rules if r['net_effect'] == 'show']
            hide_rules = [r for r in visibility_rules if r['net_effect'] == 'hide']
            
            visibility_behavior = {
                'default_state': 'visible' if always_visible else 'hidden',
                'conditional_visibility': len(visibility_rules) > 0,
                'show_rule_count': len(show_rules),
                'hide_rule_count': len(hide_rules),
                'complexity': 'simple' if len(visibility_rules) <= 1 else 'complex'
            }
            
            return {
                'step_info': {
                    'id': step_id,
                    'title': target_step.get('title'),
                    'position': target_step.get('position')
                },
                'visibility_behavior': visibility_behavior,
                'visibility_rules': visibility_rules,
                'visibility_logic': visibility_logic,
                'summary': {
                    'always_visible': always_visible,
                    'has_show_conditions': len(show_rules) > 0,
                    'has_hide_conditions': len(hide_rules) > 0,
                    'total_rules_affecting': len(visibility_rules),
                    'predictability': 'high' if len(visibility_rules) <= 2 else 'medium' if len(visibility_rules) <= 5 else 'low'
                },
                'recommendations': self._generate_visibility_recommendations(visibility_rules, always_visible)
            }
            
        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to analyze step visibility for step {step_id}: {e}")
            raise

    def suggest_automation_consolidation(self, org_id: str, template_id: str) -> List[Dict[str, Any]]:
        """
        AI analysis of automation rules with consolidation recommendations.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
        
        Returns:
            List of consolidation recommendations with detailed analysis
        """
        try:
            analysis = self.analyze_template_automations(org_id, template_id)
            template_data = self.get_template_with_steps(org_id, template_id)
            
            recommendations = []
            
            # Priority 1: Critical issues
            for conflict in analysis['conflicts']:
                recommendations.append({
                    'priority': 'critical',
                    'type': 'resolve_conflict',
                    'title': f"Resolve automation conflict between '{conflict['automation1_alias']}' and '{conflict['automation2_alias']}'",
                    'description': f"These automations have overlapping conditions (similarity: {conflict['similarity_score']:.1%}) but target the same elements",
                    'impact': 'high',
                    'effort': 'medium',
                    'automation_ids': [conflict['automation1_id'], conflict['automation2_id']],
                    'common_targets': conflict['common_targets'],
                    'recommended_action': 'Review conditions and merge or differentiate the rules',
                    'risk_if_ignored': 'Unpredictable behavior, potential process failures'
                })
            
            # Priority 2: Redundancies
            for redundancy in analysis['redundancies']:
                recommendations.append({
                    'priority': 'high',
                    'type': 'eliminate_redundancy',
                    'title': f"Merge redundant automation rules",
                    'description': f"Two automations have identical conditions but separate implementations",
                    'impact': 'medium',
                    'effort': 'low',
                    'automation_ids': [redundancy['automation1_id'], redundancy['automation2_id']],
                    'recommended_action': 'Consolidate into a single rule with combined actions',
                    'expected_benefit': 'Reduced maintenance overhead, clearer logic flow'
                })
            
            # Priority 3: Optimization opportunities
            for opportunity in analysis['optimization_opportunities']:
                if opportunity['type'] == 'merge_simple_rules':
                    recommendations.append({
                        'priority': 'medium',
                        'type': 'consolidate_simple_rules',
                        'title': f"Group {len(opportunity['automation_ids'])} simple automation rules",
                        'description': "Multiple single-condition rules could be combined into fewer, more efficient rules",
                        'impact': 'medium',
                        'effort': 'medium',
                        'automation_ids': opportunity['automation_ids'],
                        'recommended_action': 'Create multi-condition rules grouped by similar actions',
                        'expected_benefit': f"Reduce rule count by approximately {len(opportunity['automation_ids']) - 2}"
                    })
                
                elif opportunity['type'] == 'orphaned_automation':
                    recommendations.append({
                        'priority': 'high',
                        'type': 'remove_orphaned',
                        'title': f"Remove unused automation: {opportunity.get('automation_alias', 'Unknown')}",
                        'description': opportunity['description'],
                        'impact': 'low',
                        'effort': 'low',
                        'automation_ids': [opportunity['automation_id']],
                        'recommended_action': opportunity['recommendation'],
                        'expected_benefit': 'Cleaner automation setup, reduced confusion'
                    })
                
                elif opportunity['type'] == 'complex_conditions':
                    recommendations.append({
                        'priority': 'medium',
                        'type': 'simplify_complex',
                        'title': f"Simplify complex automation",
                        'description': opportunity['description'],
                        'impact': 'medium',
                        'effort': 'high',
                        'automation_ids': [opportunity['automation_id']],
                        'recommended_action': opportunity['recommendation'],
                        'expected_benefit': 'Improved maintainability and reliability'
                    })
            
            # Priority 4: General improvements
            if analysis['complexity_score'] > 70:
                recommendations.append({
                    'priority': 'low',
                    'type': 'reduce_complexity',
                    'title': f"Overall automation complexity is high (score: {analysis['complexity_score']})",
                    'description': "The template has complex automation setup that may be difficult to maintain",
                    'impact': 'medium',
                    'effort': 'high',
                    'recommended_action': 'Consider redesigning automation flow with fewer, more focused rules',
                    'expected_benefit': 'Easier maintenance, better performance, reduced errors'
                })
            
            # Sort by priority
            priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            recommendations.sort(key=lambda x: priority_order.get(x['priority'], 4))
            
            return recommendations
            
        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to suggest automation consolidation for template {template_id}: {e}")
            raise

    def _analyze_condition_similarity(self, conditions1: List, conditions2: List) -> Dict[str, Any]:
        """Helper method to analyze similarity between condition sets"""
        if not conditions1 or not conditions2:
            return {'similarity_score': 0.0, 'common_elements': []}
        
        # Compare condition elements
        elements1 = set()
        elements2 = set()
        
        for cond in conditions1:
            if hasattr(cond, 'conditionable_type') and hasattr(cond, 'conditionable_id'):
                elements1.add(f"{cond.conditionable_type}:{cond.conditionable_id}")
        
        for cond in conditions2:
            if hasattr(cond, 'conditionable_type') and hasattr(cond, 'conditionable_id'):
                elements2.add(f"{cond.conditionable_type}:{cond.conditionable_id}")
        
        if not elements1 or not elements2:
            return {'similarity_score': 0.0, 'common_elements': []}
        
        common_elements = elements1.intersection(elements2)
        similarity_score = len(common_elements) / max(len(elements1), len(elements2))
        
        return {
            'similarity_score': similarity_score,
            'common_elements': list(common_elements)
        }

    def _summarize_conditions(self, conditions: List) -> str:
        """Helper method to create human-readable condition summary"""
        if not conditions:
            return "Always"
        
        condition_parts = []
        for cond in conditions:
            if hasattr(cond, 'conditionable_type') and hasattr(cond, 'operation') and hasattr(cond, 'statement'):
                part = f"{cond.conditionable_type} {cond.operation} '{cond.statement}'"
                condition_parts.append(part)
        
        if len(condition_parts) == 1:
            return condition_parts[0]
        elif len(condition_parts) <= 3:
            return " AND ".join(condition_parts)
        else:
            return f"{condition_parts[0]} AND {len(condition_parts)-1} more conditions"

    def _generate_visibility_recommendations(self, visibility_rules: List, always_visible: bool) -> List[str]:
        """Helper method to generate visibility recommendations"""
        recommendations = []
        
        if len(visibility_rules) == 0:
            if always_visible:
                recommendations.append("Step is always visible - no optimization needed")
            else:
                recommendations.append("Step is never visible - check if this is intentional")
        
        elif len(visibility_rules) == 1:
            recommendations.append("Simple visibility logic - good maintainability")
        
        elif len(visibility_rules) > 5:
            recommendations.append("Complex visibility logic - consider simplifying conditions")
            recommendations.append("Review if all visibility rules are necessary")
        
        show_rules = [r for r in visibility_rules if r['net_effect'] == 'show']
        hide_rules = [r for r in visibility_rules if r['net_effect'] == 'hide']
        
        if len(show_rules) > 0 and len(hide_rules) > 0:
            recommendations.append("Step has both show and hide conditions - verify intended behavior")
            recommendations.append("Consider testing edge cases where multiple rules might trigger")
        
        return recommendations


    # TODO after implementing the new functions on API side
    # def add_kickoff_field(self, org_id: str, template_id: str, field_data: Dict[str, Any]) -> PrerunField:
    #     """
    #     Add kickoff/prerun fields to template.
    #
    #     Args:
    #         org_id: Organization ID
    #         template_id: Template ID
    #         field_data: Dictionary containing prerun field data including field_type, label, required, etc.
    #
    #     Returns:
    #         PrerunField object
    #
    #     Raises:
    #         TallyfyError: If the request fails
    #     """
    #     try:
    #         endpoint = f"organizations/{org_id}/checklists/{template_id}/prerun"
    #         response_data = self.sdk._make_request('POST', endpoint, data=field_data)
    #
    #         if isinstance(response_data, dict) and 'data' in response_data:
    #             prerun_data = response_data['data']
    #             return PrerunField.from_dict(prerun_data)
    #         else:
    #             self.sdk.logger.warning("Unexpected response format for kickoff field creation")
    #             return None
    #
    #     except TallyfyError as e:
    #         self.sdk.logger.error(f"Failed to add kickoff field to template {template_id}: {e}")
    #         raise
    #
    # def update_kickoff_field(self, org_id: str, template_id: str, field_id: str, **kwargs) -> PrerunField:
    #     """
    #     Update kickoff field properties.
    #
    #     Args:
    #         org_id: Organization ID
    #         template_id: Template ID
    #         field_id: Prerun field ID
    #         **kwargs: Prerun field properties to update
    #
    #     Returns:
    #         Updated PrerunField object
    #
    #     Raises:
    #         TallyfyError: If the request fails
    #     """
    #     try:
    #         endpoint = f"organizations/{org_id}/checklists/{template_id}/prerun/{field_id}"
    #
    #         # Build update data from kwargs
    #         update_data = {}
    #         allowed_fields = [
    #             'field_type', 'label', 'guidance', 'required', 'position', 'options',
    #             'validation_rules', 'default_value', 'placeholder', 'max_length',
    #             'min_length', 'regex_pattern', 'help_text'
    #         ]
    #
    #         for field, value in kwargs.items():
    #             if field in allowed_fields:
    #                 update_data[field] = value
    #             else:
    #                 self.sdk.logger.warning(f"Ignoring unknown prerun field: {field}")
    #
    #         if not update_data:
    #             raise ValueError("No valid prerun field properties provided for update")
    #
    #         response_data = self.sdk._make_request('PUT', endpoint, data=update_data)
    #
    #         if isinstance(response_data, dict) and 'data' in response_data:
    #             prerun_data = response_data['data']
    #             return PrerunField.from_dict(prerun_data)
    #         else:
    #             self.sdk.logger.warning("Unexpected response format for kickoff field update")
    #             return None
    #
    #     except TallyfyError as e:
    #         self.sdk.logger.error(f"Failed to update kickoff field {field_id}: {e}")
    #         raise

    def suggest_kickoff_fields(self, org_id: str, template_id: str) -> List[Dict[str, Any]]:
        """
        Suggest relevant kickoff fields based on template analysis.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
        
        Returns:
            List of suggested kickoff field configurations with reasoning
        """
        try:
            # Get template details for analysis
            template_data = self.get_template_with_steps(org_id, template_id)
            if not template_data:
                raise TallyfyError(f"Could not retrieve template {template_id}")
            
            template = template_data['template']
            steps = template_data.get('steps', [])
            existing_prerun = template.prerun or []
            
            # Analyze template content for suggestions
            suggestions = []
            confidence_scores = {}
            
            # Common fields based on template type and content
            template_title = template.title.lower()
            template_summary = (template.summary or '').lower()
            template_content = f"{template_title} {template_summary}"
            
            # Basic project information fields
            if any(word in template_content for word in ['project', 'initiative', 'campaign', 'launch']):
                suggestions.append({
                    'field_type': 'text',
                    'label': 'Project Name',
                    'guidance': 'Enter the name of this project or initiative',
                    'required': True,
                    'position': 1,
                    'reasoning': 'Project-related templates benefit from capturing the specific project name',
                    'confidence': 'high'
                })
                confidence_scores['project_name'] = 0.9
                
                suggestions.append({
                    'field_type': 'date',
                    'label': 'Target Completion Date',
                    'guidance': 'When should this project be completed?',
                    'required': False,
                    'position': 2,
                    'reasoning': 'Project templates often need target completion dates for planning',
                    'confidence': 'medium'
                })
                confidence_scores['target_date'] = 0.7
            
            # Client/customer information
            if any(word in template_content for word in ['client', 'customer', 'vendor', 'supplier', 'partner']):
                suggestions.append({
                    'field_type': 'text',
                    'label': 'Client/Customer Name',
                    'guidance': 'Name of the client or customer for this process',
                    'required': True,
                    'position': len(suggestions) + 1,
                    'reasoning': 'Client-focused templates need client identification',
                    'confidence': 'high'
                })
                confidence_scores['client_name'] = 0.9
                
                suggestions.append({
                    'field_type': 'email',
                    'label': 'Primary Contact Email',
                    'guidance': 'Main contact person for this engagement',
                    'required': False,
                    'position': len(suggestions) + 1,
                    'reasoning': 'Client processes benefit from capturing contact information',
                    'confidence': 'medium'
                })
                confidence_scores['contact_email'] = 0.7
            
            # Budget/financial fields
            if any(word in template_content for word in ['budget', 'cost', 'expense', 'financial', 'price', 'payment']):
                suggestions.append({
                    'field_type': 'number',
                    'label': 'Budget Amount',
                    'guidance': 'Total budget allocated for this initiative',
                    'required': False,
                    'position': len(suggestions) + 1,
                    'validation_rules': {'min': 0},
                    'reasoning': 'Financial templates should capture budget information upfront',
                    'confidence': 'high'
                })
                confidence_scores['budget'] = 0.85
            
            # Priority/urgency fields
            if any(word in template_content for word in ['urgent', 'priority', 'critical', 'important', 'emergency']):
                suggestions.append({
                    'field_type': 'dropdown',
                    'label': 'Priority Level',
                    'guidance': 'How urgent is this request?',
                    'required': True,
                    'position': len(suggestions) + 1,
                    'options': [
                        {'value': 'low', 'label': 'Low Priority'},
                        {'value': 'medium', 'label': 'Medium Priority'},
                        {'value': 'high', 'label': 'High Priority'},
                        {'value': 'urgent', 'label': 'Urgent'}
                    ],
                    'reasoning': 'Templates with urgency keywords benefit from priority classification',
                    'confidence': 'medium'
                })
                confidence_scores['priority'] = 0.75
            
            # Department/team fields
            if any(word in template_content for word in ['department', 'team', 'division', 'group', 'unit']):
                suggestions.append({
                    'field_type': 'text',
                    'label': 'Department/Team',
                    'guidance': 'Which department or team is this for?',
                    'required': False,
                    'position': len(suggestions) + 1,
                    'reasoning': 'Organizational templates often need department identification',
                    'confidence': 'medium'
                })
                confidence_scores['department'] = 0.6
            
            # Description field for complex processes
            if len(steps) > 5:
                suggestions.append({
                    'field_type': 'wysiwyg',
                    'label': 'Detailed Description',
                    'guidance': 'Provide detailed context and requirements for this process',
                    'required': False,
                    'position': len(suggestions) + 1,
                    'reasoning': 'Complex templates with many steps benefit from detailed upfront descriptions',
                    'confidence': 'medium'
                })
                confidence_scores['description'] = 0.65
            
            # Check for steps that might benefit from kickoff information
            step_analysis = {
                'requires_approval': False,
                'has_external_dependencies': False,
                'requires_assets': False
            }
            
            for step in steps['data']:
                step_title = step.get('title', '')
                step_summary = step.get('summary', '')

                if step_title:
                    step_title = step_title.lower()
                if step_summary:
                    step_summary = step_summary.lower()

                step_content = f"{step_title} {step_summary}"
                
                if any(word in step_content for word in ['approve', 'review', 'authorize', 'sign-off']):
                    step_analysis['requires_approval'] = True
                
                if any(word in step_content for word in ['external', 'vendor', 'third-party', 'client']):
                    step_analysis['has_external_dependencies'] = True
                
                if any(word in step_content for word in ['upload', 'attach', 'document', 'file', 'image']):
                    step_analysis['requires_assets'] = True
            
            # Add suggestions based on step analysis
            if step_analysis['requires_approval']:
                suggestions.append({
                    'field_type': 'dropdown',
                    'label': 'Approval Required',
                    'guidance': 'Does this process require special approval?',
                    'required': False,
                    'position': len(suggestions) + 1,
                    'options': [
                        {'value': 'none', 'label': 'No special approval needed'},
                        {'value': 'manager', 'label': 'Manager approval required'},
                        {'value': 'director', 'label': 'Director approval required'},
                        {'value': 'executive', 'label': 'Executive approval required'}
                    ],
                    'reasoning': 'Template contains approval steps that may need upfront specification',
                    'confidence': 'medium'
                })
                confidence_scores['approval_type'] = 0.7
            
            if step_analysis['has_external_dependencies']:
                suggestions.append({
                    'field_type': 'text',
                    'label': 'External Dependencies',
                    'guidance': 'List any external parties or dependencies involved',
                    'required': False,
                    'position': len(suggestions) + 1,
                    'reasoning': 'Template has external dependencies that should be identified upfront',
                    'confidence': 'medium'
                })
                confidence_scores['external_deps'] = 0.65
            
            # Filter out suggestions that would duplicate existing fields
            existing_labels = set((field.label or '').lower() for field in existing_prerun)
            filtered_suggestions = []
            
            for suggestion in suggestions:
                if suggestion['label'].lower() not in existing_labels:
                    # Add similarity check for existing fields
                    is_similar = False
                    for existing_field in existing_prerun:
                        if existing_field.label and self._calculate_field_similarity(suggestion['label'], existing_field.label) > 0.8:
                            is_similar = True
                            break
                    
                    if not is_similar:
                        filtered_suggestions.append(suggestion)
            
            # Sort by confidence score
            filtered_suggestions.sort(key=lambda x: confidence_scores.get(x.get('_key', ''), 0.5), reverse=True)
            
            # Limit to top 5 suggestions
            return filtered_suggestions[:5]
            
        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to suggest kickoff fields for template {template_id}: {e}")
            raise

    def _calculate_field_similarity(self, label1: str, label2: str) -> float:
        """Helper method to calculate similarity between field labels"""
        label1_words = set(label1.lower().split())
        label2_words = set(label2.lower().split())
        
        if not label1_words or not label2_words:
            return 0.0
        
        intersection = label1_words.intersection(label2_words)
        union = label1_words.union(label2_words)
        
        return len(intersection) / len(union) if union else 0.0

    def assess_template_health(self, org_id: str, template_id: str) -> Dict[str, Any]:
        """
        Comprehensive template health check analyzing multiple aspects.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
        
        Returns:
            Dictionary containing:
            - overall_health_score: Score from 0-100
            - health_categories: Breakdown by category
            - issues: List of identified problems
            - recommendations: Improvement suggestions
            - improvement_plan: Prioritized action items
        """
        try:
            # Get comprehensive template data
            template_data = self.get_template_with_steps(org_id, template_id)
            if not template_data:
                raise TallyfyError(f"Could not retrieve template {template_id}")
            
            template = template_data['template']
            steps = template_data.get('steps', [])
            steps = steps['data']
            # Initialize health assessment
            health_assessment = {
                'overall_health_score': 0,
                'health_categories': {},
                'issues': [],
                'recommendations': [],
                'improvement_plan': [],
                'assessment_details': {
                    'template_info': {
                        'id': template.id,
                        'title': template.title,
                        'step_count': len(steps),
                        'automation_count': len(template.automated_actions or []),
                        'prerun_field_count': len(template.prerun or [])
                    },
                    'analysis_timestamp': self._get_current_timestamp()
                }
            }
            
            # 1. Template Metadata Health (15 points)
            metadata_score, metadata_issues, metadata_recommendations = self._assess_template_metadata(template)
            health_assessment['health_categories']['metadata'] = {
                'score': metadata_score,
                'max_score': 15,
                'description': 'Template title, summary, and basic configuration'
            }
            health_assessment['issues'].extend(metadata_issues)
            health_assessment['recommendations'].extend(metadata_recommendations)
            
            # 2. Step Title Clarity (20 points)
            clarity_score, clarity_issues, clarity_recommendations = self._assess_step_clarity(steps)
            health_assessment['health_categories']['step_clarity'] = {
                'score': clarity_score,
                'max_score': 20,
                'description': 'Clarity and descriptiveness of step titles'
            }
            health_assessment['issues'].extend(clarity_issues)
            health_assessment['recommendations'].extend(clarity_recommendations)
            
            # 3. Form Field Completeness (15 points)
            form_score, form_issues, form_recommendations = self._assess_form_completeness(steps)
            health_assessment['health_categories']['form_fields'] = {
                'score': form_score,
                'max_score': 15,
                'description': 'Quality and completeness of form fields'
            }
            health_assessment['issues'].extend(form_issues)
            health_assessment['recommendations'].extend(form_recommendations)
            
            # 4. Automation Efficiency (20 points)
            automation_score, automation_issues, automation_recommendations = self._assess_automation_efficiency(template, template_id, org_id)
            health_assessment['health_categories']['automation'] = {
                'score': automation_score,
                'max_score': 20,
                'description': 'Automation rules efficiency and conflicts'
            }
            health_assessment['issues'].extend(automation_issues)
            health_assessment['recommendations'].extend(automation_recommendations)
            
            # 5. Deadline Reasonableness (15 points)
            deadline_score, deadline_issues, deadline_recommendations = self._assess_deadline_reasonableness(steps)
            health_assessment['health_categories']['deadlines'] = {
                'score': deadline_score,
                'max_score': 15,
                'description': 'Appropriateness of step deadlines'
            }
            health_assessment['issues'].extend(deadline_issues)
            health_assessment['recommendations'].extend(deadline_recommendations)
            
            # 6. Workflow Logic (15 points)
            workflow_score, workflow_issues, workflow_recommendations = self._assess_workflow_logic(steps, template.automated_actions or [])
            health_assessment['health_categories']['workflow_logic'] = {
                'score': workflow_score,
                'max_score': 15,
                'description': 'Overall workflow structure and logic'
            }
            health_assessment['issues'].extend(workflow_issues)
            health_assessment['recommendations'].extend(workflow_recommendations)
            
            # Calculate overall health score
            total_score = sum(cat['score'] for cat in health_assessment['health_categories'].values())
            max_total_score = sum(cat['max_score'] for cat in health_assessment['health_categories'].values())
            health_assessment['overall_health_score'] = round((total_score / max_total_score) * 100, 1)
            
            # Generate improvement plan
            health_assessment['improvement_plan'] = self._generate_improvement_plan(
                health_assessment['issues'], 
                health_assessment['recommendations'],
                health_assessment['health_categories']
            )
            
            # Add health rating
            health_assessment['health_rating'] = self._get_health_rating(health_assessment['overall_health_score'])
            
            return health_assessment
            
        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to assess template health for template {template_id}: {e}")
            raise

    def _assess_template_metadata(self, template) -> tuple:
        """Assess template metadata quality"""
        score = 0
        issues = []
        recommendations = []
        
        # Title quality (5 points)
        if template.title and len(template.title.strip()) > 0:
            if len(template.title.strip()) >= 10:
                score += 5
            elif len(template.title.strip()) >= 5:
                score += 3
                issues.append({
                    'category': 'metadata',
                    'severity': 'medium',
                    'issue': 'Template title is quite short',
                    'description': f"Title '{template.title}' could be more descriptive"
                })
                recommendations.append({
                    'category': 'metadata',
                    'priority': 'medium',
                    'action': 'Expand template title',
                    'description': 'Consider adding more descriptive words to clarify the template purpose'
                })
            else:
                score += 1
                issues.append({
                    'category': 'metadata',
                    'severity': 'high',
                    'issue': 'Template title is very short',
                    'description': f"Title '{template.title}' is too brief and unclear"
                })
                recommendations.append({
                    'category': 'metadata',
                    'priority': 'high',
                    'action': 'Rewrite template title',
                    'description': 'Create a clear, descriptive title that explains what this template accomplishes'
                })
        else:
            issues.append({
                'category': 'metadata',
                'severity': 'critical',
                'issue': 'Missing template title',
                'description': 'Template has no title or empty title'
            })
            recommendations.append({
                'category': 'metadata',
                'priority': 'critical',
                'action': 'Add template title',
                'description': 'Every template must have a clear, descriptive title'
            })
        
        # Summary quality (5 points)
        if template.summary and len(template.summary.strip()) > 0:
            if len(template.summary.strip()) >= 50:
                score += 5
            elif len(template.summary.strip()) >= 20:
                score += 3
                recommendations.append({
                    'category': 'metadata',
                    'priority': 'low',
                    'action': 'Expand template summary',
                    'description': 'Consider adding more detail to help users understand the template purpose'
                })
            else:
                score += 2
                issues.append({
                    'category': 'metadata',
                    'severity': 'medium',
                    'issue': 'Template summary is very brief',
                    'description': 'Summary should provide more context about the template'
                })
                recommendations.append({
                    'category': 'metadata',
                    'priority': 'medium',
                    'action': 'Improve template summary',
                    'description': 'Write a more comprehensive summary explaining when and how to use this template'
                })
        else:
            issues.append({
                'category': 'metadata',
                'severity': 'high',
                'issue': 'Missing template summary',
                'description': 'Template lacks a summary description'
            })
            recommendations.append({
                'category': 'metadata',
                'priority': 'high',
                'action': 'Add template summary',
                'description': 'Write a clear summary explaining the template purpose and scope'
            })
        
        # Guidance quality (5 points)
        if template.guidance and len(template.guidance.strip()) > 0:
            score += 5
        else:
            score += 2
            recommendations.append({
                'category': 'metadata',
                'priority': 'low',
                'action': 'Add template guidance',
                'description': 'Consider adding guidance to help users understand how to use this template effectively'
            })
        
        return score, issues, recommendations

    def _assess_step_clarity(self, steps) -> tuple:
        """Assess step title clarity and descriptiveness"""
        score = 0
        issues = []
        recommendations = []
        
        if not steps:
            issues.append({
                'category': 'step_clarity',
                'severity': 'critical',
                'issue': 'Template has no steps',
                'description': 'Template must have at least one step to be functional'
            })
            recommendations.append({
                'category': 'step_clarity',
                'priority': 'critical',
                'action': 'Add steps to template',
                'description': 'Create workflow steps that define the process'
            })
            return 0, issues, recommendations
        
        total_possible = len(steps) * 4  # 4 points per step max
        step_scores = []
        
        for i, step in enumerate(steps):
            step_score = 0
            step_title = step.get('title', '')
            step_summary = step.get('summary', '')
            if step_title:
                step_title = step_title.strip()
            if step_summary:
                step_summary = step_summary.strip()
            
            # Title existence and quality (3 points)
            if step_title:
                if len(step_title) >= 15:
                    step_score += 3
                elif len(step_title) >= 8:
                    step_score += 2
                elif len(step_title) >= 3:
                    step_score += 1
                    issues.append({
                        'category': 'step_clarity',
                        'severity': 'medium',
                        'issue': f'Step {i+1} title is too brief',
                        'description': f"Step title '{step_title}' could be more descriptive"
                    })
                    recommendations.append({
                        'category': 'step_clarity',
                        'priority': 'medium',
                        'action': f'Improve step {i+1} title',
                        'description': 'Make the title more descriptive and action-oriented'
                    })
                else:
                    issues.append({
                        'category': 'step_clarity',
                        'severity': 'high',
                        'issue': f'Step {i+1} title is very unclear',
                        'description': f"Step title '{step_title}' is too short to be meaningful"
                    })
                    recommendations.append({
                        'category': 'step_clarity',
                        'priority': 'high',
                        'action': f'Rewrite step {i+1} title',
                        'description': 'Create a clear, action-oriented title that explains what needs to be done'
                    })
                
                # Check for action words
                action_words = ['create', 'review', 'approve', 'complete', 'submit', 'verify', 'analyze', 'prepare', 'send', 'update']
                if any(word in step_title.lower() for word in action_words):
                    # Bonus for action-oriented titles
                    step_score += 0.5
            else:
                issues.append({
                    'category': 'step_clarity',
                    'severity': 'critical',
                    'issue': f'Step {i+1} has no title',
                    'description': 'Every step must have a clear title'
                })
                recommendations.append({
                    'category': 'step_clarity',
                    'priority': 'critical',
                    'action': f'Add title to step {i+1}',
                    'description': 'Write a clear, action-oriented title for this step'
                })
            
            # Summary quality (1 point)
            if step_summary and len(step_summary) >= 20:
                step_score += 1
            elif not step_summary:
                recommendations.append({
                    'category': 'step_clarity',
                    'priority': 'low',
                    'action': f'Add summary to step {i+1}',
                    'description': 'Consider adding a summary to provide additional context'
                })
            
            step_scores.append(min(step_score, 4))  # Cap at 4 points per step
        
        # Calculate score as percentage of maximum, scaled to 20 points
        if total_possible > 0:
            score = round((sum(step_scores) / total_possible) * 20)
        
        return score, issues, recommendations

    def _assess_form_completeness(self, steps) -> tuple:
        """Assess form field quality and completeness"""
        score = 0
        issues = []
        recommendations = []
        
        total_fields = 0
        well_configured_fields = 0
        steps_with_forms = 0
        
        for i, step in enumerate(steps):
            captures = step.get('captures', [])
            if captures:
                steps_with_forms += 1
                
            for j, capture in enumerate(captures):
                total_fields += 1
                field_score = 0
                
                # Field has label (required)
                label = capture.get('label', '').strip()
                if label:
                    if len(label) >= 3:
                        field_score += 2
                    else:
                        issues.append({
                            'category': 'form_fields',
                            'severity': 'medium',
                            'issue': f'Step {i+1} field {j+1} has very short label',
                            'description': f"Field label '{label}' is too brief"
                        })
                        field_score += 1
                else:
                    issues.append({
                        'category': 'form_fields',
                        'severity': 'high',
                        'issue': f'Step {i+1} field {j+1} missing label',
                        'description': 'Form field must have a descriptive label'
                    })
                    recommendations.append({
                        'category': 'form_fields',
                        'priority': 'high',
                        'action': f'Add label to step {i+1} field {j+1}',
                        'description': 'Every form field needs a clear, descriptive label'
                    })

                # Field has guidance
                guidance = capture.get('guidance', '')
                if guidance and len(guidance) >= 10:
                    field_score += 1
                elif not guidance:
                    recommendations.append({
                        'category': 'form_fields',
                        'priority': 'low',
                        'action': f'Add guidance to step {i+1} field {j+1}',
                        'description': 'Consider adding guidance to help users understand what to enter'
                    })
                
                # Required field properly marked
                field_type = capture.get('field_type', '')
                if capture.get('required') is not None:
                    field_score += 1
                
                # Field type specific checks
                if field_type == 'dropdown':
                    options = capture.get('options', [])
                    if options and len(options) >= 2:
                        field_score += 1
                    else:
                        issues.append({
                            'category': 'form_fields',
                            'severity': 'high',
                            'issue': f'Step {i+1} dropdown field has insufficient options',
                            'description': 'Dropdown fields should have at least 2 options'
                        })
                        recommendations.append({
                            'category': 'form_fields',
                            'priority': 'high',
                            'action': f'Add options to step {i+1} dropdown field',
                            'description': 'Configure appropriate dropdown options for user selection'
                        })
                elif field_type in ['text', 'wysiwyg']:
                    field_score += 1  # Text fields are generally well-configured by default
                
                if field_score >= 4:
                    well_configured_fields += 1
        
        # Calculate score
        if total_fields > 0:
            field_quality_ratio = well_configured_fields / total_fields
            score = round(field_quality_ratio * 15)
        else:
            score = 10  # No form fields is not necessarily bad
            if len(steps) > 2:  # But if there are many steps, might expect some forms
                recommendations.append({
                    'category': 'form_fields',
                    'priority': 'medium',
                    'action': 'Consider adding form fields',
                    'description': 'Templates with multiple steps often benefit from data collection forms'
                })
        
        return score, issues, recommendations

    def _assess_automation_efficiency(self, template, template_id, org_id) -> tuple:
        """Assess automation rules for efficiency and conflicts"""
        score = 0
        issues = []
        recommendations = []
        
        automations = template.automated_actions or []
        
        if not automations:
            score = 15  # No automations is fine for simple templates
            recommendations.append({
                'category': 'automation',
                'priority': 'low',
                'action': 'Consider adding automation',
                'description': 'Automation can improve efficiency for repetitive workflows'
            })
            return score, issues, recommendations
        
        try:
            # Use existing automation analysis
            analysis = self.analyze_template_automations(org_id, template_id)
            base_score = 20
            
            # Deduct for conflicts
            conflicts = analysis.get('conflicts', [])
            if conflicts:
                deduction = min(len(conflicts) * 3, 10)
                base_score -= deduction
                for conflict in conflicts:
                    issues.append({
                        'category': 'automation',
                        'severity': 'high',
                        'issue': 'Automation conflict detected',
                        'description': f"Conflicting automations: {conflict.get('automation1_alias')} and {conflict.get('automation2_alias')}"
                    })
                    recommendations.append({
                        'category': 'automation',
                        'priority': 'high',
                        'action': 'Resolve automation conflicts',
                        'description': 'Review and merge or differentiate conflicting automation rules'
                    })

            # Deduct for redundancies
            redundancies = analysis.get('redundancies', [])
            if redundancies:
                deduction = min(len(redundancies) * 2, 5)
                base_score -= deduction
                for redundancy in redundancies:
                    issues.append({
                        'category': 'automation',
                        'severity': 'medium',
                        'issue': 'Redundant automation rules',
                        'description': 'Multiple automation rules with identical conditions'
                    })
                    recommendations.append({
                        'category': 'automation',
                        'priority': 'medium',
                        'action': 'Consolidate redundant automations',
                        'description': 'Merge automation rules with identical conditions'
                    })

            # Check complexity
            complexity_score = analysis.get('complexity_score', 0)
            if complexity_score > 80:
                base_score -= 3
                issues.append({
                    'category': 'automation',
                    'severity': 'medium',
                    'issue': 'High automation complexity',
                    'description': f'Complexity score of {complexity_score} may be difficult to maintain'
                })
                recommendations.append({
                    'category': 'automation',
                    'priority': 'medium',
                    'action': 'Simplify automation rules',
                    'description': 'Consider breaking complex rules into simpler, more focused automations'
                })

            score = max(base_score, 0000)
            
        except Exception as e:
            # If automation analysis fails, give a neutral score
            score = 10
            self.sdk.logger.warning(f"Could not analyze automation efficiency: {e}")
        
        return score, issues, recommendations

    def _assess_deadline_reasonableness(self, steps) -> tuple:
        """Assess whether step deadlines are reasonable"""
        score = 0
        issues = []
        recommendations = []
        
        steps_with_deadlines = 0
        reasonable_deadlines = 0
        
        for i, step in enumerate(steps):
            deadline = step.get('deadline')
            if deadline and isinstance(deadline, dict):
                steps_with_deadlines += 1
                
                value = deadline.get('value', 0)
                unit = deadline.get('unit', 'days')
                
                # Convert to hours for comparison
                hours = value
                if unit == 'days':
                    hours = value * 24
                elif unit == 'weeks':
                    hours = value * 24 * 7
                elif unit == 'months':
                    hours = value * 24 * 30
                elif unit == 'business_days':
                    hours = value * 8  # 8 hour work days
                
                # Assess reasonableness based on step content
                step_title = step.get('title', '')
                step_summary = step.get('summary', '')
                if step_summary:
                    step_summary = step_summary.lower()
                if step_title:
                    step_title = step_title.lower()
                content = f"{step_title} {step_summary}"
                
                is_reasonable = True
                
                # Quick tasks should have short deadlines
                if any(word in content for word in ['approve', 'review', 'check', 'verify', 'confirm']):
                    if hours > 72:  # More than 3 days
                        is_reasonable = False
                        issues.append({
                            'category': 'deadlines',
                            'severity': 'medium',
                            'issue': f'Step {i+1} deadline may be too long',
                            'description': f'Quick approval tasks typically need shorter deadlines than {value} {unit}'
                        })
                        recommendations.append({
                            'category': 'deadlines',
                            'priority': 'medium',
                            'action': f'Shorten deadline for step {i+1}',
                            'description': 'Consider 1-2 business days for approval tasks'
                        })
                
                # Complex tasks should have adequate time
                elif any(word in content for word in ['develop', 'create', 'design', 'write', 'prepare', 'analyze']):
                    if hours < 16:  # Less than 2 days
                        is_reasonable = False
                        issues.append({
                            'category': 'deadlines',
                            'severity': 'medium',
                            'issue': f'Step {i+1} deadline may be too short',
                            'description': f'Creative/development work may need more time than {value} {unit}'
                        })
                        recommendations.append({
                            'category': 'deadlines',
                            'priority': 'medium',
                            'action': f'Extend deadline for step {i+1}',
                            'description': 'Consider 3-5 days or 1 week for complex creative work'
                        })
                
                # Extremely short or long deadlines
                if hours < 1:
                    is_reasonable = False
                    issues.append({
                        'category': 'deadlines',
                        'severity': 'high',
                        'issue': f'Step {i+1} deadline is extremely short',
                        'description': f'Deadline of {value} {unit} is likely unrealistic'
                    })
                elif hours > 720:  # More than 30 days
                    is_reasonable = False
                    issues.append({
                        'category': 'deadlines',
                        'severity': 'medium',
                        'issue': f'Step {i+1} deadline is very long',
                        'description': f'Consider if {value} {unit} is appropriate for maintaining momentum'
                    })
                    recommendations.append({
                        'category': 'deadlines',
                        'priority': 'low',
                        'action': f'Review long deadline for step {i+1}',
                        'description': 'Very long deadlines can reduce urgency and momentum'
                    })
                
                if is_reasonable:
                    reasonable_deadlines += 1
        
        # Calculate score
        if steps_with_deadlines > 0:
            ratio = reasonable_deadlines / steps_with_deadlines
            score = round(ratio * 15)
        else:
            score = 10  # Neutral score if no deadlines set
            if len(steps) > 1:
                recommendations.append({
                    'category': 'deadlines',
                    'priority': 'medium',
                    'action': 'Consider adding deadlines',
                    'description': 'Deadlines help ensure timely completion of workflow steps'
                })
        
        return score, issues, recommendations

    def _assess_workflow_logic(self, steps, automations) -> tuple:
        """Assess overall workflow structure and logic"""
        score = 0
        issues = []
        recommendations = []
        
        # Base score
        base_score = 15
        
        # Check step count
        step_count = len(steps)
        if step_count == 0:
            issues.append({
                'category': 'workflow_logic',
                'severity': 'critical',
                'issue': 'No workflow steps defined',
                'description': 'Template must have at least one step'
            })
            return 0, issues, recommendations
        elif step_count == 1:
            base_score -= 2
            recommendations.append({
                'category': 'workflow_logic',
                'priority': 'low',
                'action': 'Consider multi-step workflow',
                'description': 'Single-step templates may benefit from being broken into multiple steps'
            })
        elif step_count > 20:
            base_score -= 3
            issues.append({
                'category': 'workflow_logic',
                'severity': 'medium',
                'issue': 'Very complex workflow',
                'description': f'Template has {step_count} steps, which may be overwhelming'
            })
            recommendations.append({
                'category': 'workflow_logic',
                'priority': 'medium',
                'action': 'Consider breaking into sub-workflows',
                'description': 'Large workflows can be divided into smaller, focused templates'
            })
        
        # Check for logical step progression
        step_titles = [step.get('title', '').lower() for step in steps]
        
        # Look for logical patterns
        has_start_step = any('start' in title or 'begin' in title or 'initiate' in title for title in step_titles)
        has_end_step = any('complete' in title or 'finish' in title or 'close' in title or 'final' in title for title in step_titles)
        
        if step_count >= 3:
            if has_start_step:
                score += 1
            if has_end_step:
                score += 1
            
            if not has_start_step and not has_end_step:
                recommendations.append({
                    'category': 'workflow_logic',
                    'priority': 'low',
                    'action': 'Consider clear start/end steps',
                    'description': 'Clear initiation and completion steps improve workflow clarity'
                })
        
        # Check automation alignment with workflow
        if automations:
            automation_targets = set()
            for automation in automations:
                for action in automation.then_actions:
                    if hasattr(action, 'target_step_id') and action.target_step_id:
                        automation_targets.add(action.target_step_id)
            
            step_ids = set(step.get('id') for step in steps if step.get('id'))
            orphaned_automations = automation_targets - step_ids
            
            if orphaned_automations:
                base_score -= 2
                issues.append({
                    'category': 'workflow_logic',
                    'severity': 'high',
                    'issue': 'Automations target non-existent steps',
                    'description': f'{len(orphaned_automations)} automation(s) target deleted or missing steps'
                })
                recommendations.append({
                    'category': 'workflow_logic',
                    'priority': 'high',
                    'action': 'Fix automation targets',
                    'description': 'Update or remove automations that target non-existent steps'
                })
        
        # Check for balanced step distribution
        steps_with_content = sum(1 for step in steps if step.get('summary') or step.get('captures'))
        if step_count > 3 and steps_with_content < step_count * 0.5:
            base_score -= 2
            recommendations.append({
                'category': 'workflow_logic',
                'priority': 'medium',
                'action': 'Add content to workflow steps',
                'description': 'Many steps lack descriptions or form fields that could help users'
            })
        
        score = max(base_score, 0)
        return score, issues, recommendations

    def _generate_improvement_plan(self, issues, recommendations, health_categories) -> List[Dict[str, Any]]:
        """Generate prioritized improvement plan"""
        plan_items = []
        
        # Critical issues first
        critical_items = [item for item in issues if item.get('severity') == 'critical']
        for item in critical_items:
            plan_items.append({
                'priority': 1,
                'category': item['category'],
                'action': f"CRITICAL: {item['issue']}",
                'description': item['description'],
                'impact': 'high',
                'effort': 'medium'
            })
        
        # High priority recommendations
        high_priority_recs = [item for item in recommendations if item.get('priority') == 'critical' or item.get('priority') == 'high']
        for item in high_priority_recs:
            plan_items.append({
                'priority': 2,
                'category': item['category'],
                'action': item['action'],
                'description': item['description'],
                'impact': 'high' if item.get('priority') == 'critical' else 'medium',
                'effort': 'medium'
            })
        
        # Focus on lowest scoring categories
        sorted_categories = sorted(health_categories.items(), key=lambda x: x[1]['score'])
        for category_name, category_data in sorted_categories[:2]:  # Top 2 lowest scoring
            if category_data['score'] < category_data['max_score'] * 0.7:  # Less than 70%
                category_recs = [item for item in recommendations if item.get('category') == category_name and item.get('priority') in ['medium', 'low']]
                for item in category_recs[:2]:  # Top 2 recommendations per category
                    plan_items.append({
                        'priority': 3,
                        'category': item['category'],
                        'action': item['action'],
                        'description': item['description'],
                        'impact': 'medium',
                        'effort': 'low' if item.get('priority') == 'low' else 'medium'
                    })
        
        # Limit to top 8 items to keep focused
        return plan_items[:8]

    def _get_health_rating(self, score) -> str:
        """Convert numeric score to health rating"""
        if score >= 90:
            return 'excellent'
        elif score >= 80:
            return 'good'
        elif score >= 70:
            return 'fair'
        elif score >= 60:
            return 'poor'
        else:
            return 'critical'

    def _get_current_timestamp(self) -> str:
        """Get current timestamp for assessment"""
        from datetime import datetime
        return datetime.now().isoformat()

    def add_assignees_to_step(self, org_id: str, template_id: str, step_id: str, assignees: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add assignees to a specific step in a template.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            step_id: Step ID to add assignees to
            assignees: Dictionary containing assignee data with users and guests
                Expected format: {
                    'assignees': [user_id1, user_id2, ...],  # List of user IDs
                    'guests': [guest_email1, guest_email2, ...]  # List of guest emails
                }
        
        Returns:
            Dictionary containing updated step information
            
        Raises:
            TallyfyError: If the request fails
        """
        try:
            endpoint = f"organizations/{org_id}/checklists/{template_id}/steps/{step_id}"
            
            # Validate assignees data
            if not isinstance(assignees, dict):
                raise ValueError("Assignees must be a dictionary")
            
            # Build update data with proper structure
            update_data = {}
            
            # Add user assignees if provided
            if 'assignees' in assignees and assignees['assignees']:
                user_ids = assignees['assignees']
                if not isinstance(user_ids, list):
                    raise ValueError("Assignees must be a list of user IDs")
                
                # Validate user IDs are integers
                for user_id in user_ids:
                    if not isinstance(user_id, int):
                        raise ValueError(f"User ID {user_id} must be an integer")
                
                update_data['assignees'] = user_ids
            
            # Add guest assignees if provided
            if 'guests' in assignees and assignees['guests']:
                guest_emails = assignees['guests']
                if not isinstance(guest_emails, list):
                    raise ValueError("Guests must be a list of email addresses")
                
                # Validate guest emails
                import re
                email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
                for guest_email in guest_emails:
                    if not isinstance(guest_email, str) or not re.match(email_pattern, guest_email):
                        raise ValueError(f"Guest email {guest_email} is not a valid email address")
                
                update_data['guests'] = guest_emails
            
            # Validate that at least one assignee type is provided
            if not update_data:
                raise ValueError("At least one assignee (user or guest) must be specified")
            
            response_data = self.sdk._make_request('PUT', endpoint, data=update_data)
            
            if isinstance(response_data, dict):
                return response_data
            else:
                self.sdk.logger.warning("Unexpected response format for step assignee addition")
                return {'success': True, 'assignees_added': update_data}
                
        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to add assignees to step {step_id}: {e}")
            raise
        except ValueError as e:
            self.sdk.logger.error(f"Invalid assignee data: {e}")
            raise TallyfyError(f"Invalid assignee data: {e}")

    def edit_description_on_step(self, org_id: str, template_id: str, step_id: str, description: str) -> Dict[str, Any]:
        """
        Edit the description/summary of a specific step in a template.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            step_id: Step ID to edit description for
            description: New description/summary text for the step
        
        Returns:
            Dictionary containing updated step information
            
        Raises:
            TallyfyError: If the request fails
        """
        try:
            endpoint = f"organizations/{org_id}/checklists/{template_id}/steps/{step_id}"
            
            # Validate description
            if not isinstance(description, str):
                raise ValueError("Description must be a string")
            
            description = description.strip()
            if not description:
                raise ValueError("Description cannot be empty")
            
            # Update data with correct payload structure
            update_data = {
                'summary': description
            }
            
            response_data = self.sdk._make_request('PUT', endpoint, data=update_data)
            
            if isinstance(response_data, dict):
                if 'data' in response_data:
                    return response_data['data']
                return response_data
            else:
                self.sdk.logger.warning("Unexpected response format for step description update")
                return {'success': True, 'updated_summary': description}
                
        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to update step description for step {step_id}: {e}")
            raise
        except ValueError as e:
            self.sdk.logger.error(f"Invalid description data: {e}")
            raise TallyfyError(f"Invalid description data: {e}")

    def add_step_to_template(self, org_id: str, template_id: str, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new step to a template.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            step_data: Dictionary containing step data including title, summary, position, etc.
                Expected format: {
                    'title': 'Step title',
                    'prevent_guest_comment': False,  # prevent guest comments
                    'allow_guest_owners': False,  # allow guest assignees
                    'can_complete_only_assignees': False,  # only assignees can complete
                    'checklist_id': 'Template ID',
                    'is_soft_start_date': True,  # soft start date
                    'everyone_must_complete': False,  # all assignees must complete
                    'skip_start_process': False,  # skip when starting process
                    'summary': 'Step description (optional)',
                    'position': 1,  # Position in workflow (optional, defaults to end)
                    'step_type': 'task',  # Optional: 'task', 'decision', 'form', etc.
                    'max_assignable': 1,  # Optional: max number of assignees
                    'webhook': 'url',  # Optional: webhook URL
                    'assignees': [123, 456],  # Optional: list of user IDs
                    'guests': ['email@example.com'],  # Optional: list of guest emails
                    'roles': ['Project Manager'],  # Optional: list of roles
                    'role_changes_every_time': True  # Optional: role changes each time
                }
        
        Returns:
            Dictionary containing created step information
            
        Raises:
            TallyfyError: If the request fails
        """
        try:
            endpoint = f"organizations/{org_id}/checklists/{template_id}/steps"
            
            # Validate step data
            if not isinstance(step_data, dict):
                raise ValueError("Step data must be a dictionary")
            
            # Validate required fields
            if 'title' not in step_data or not step_data['title']:
                raise ValueError("Step title is required")
            
            title = step_data['title'].strip()
            if not title:
                raise ValueError("Step title cannot be empty")
            
            # Build step creation data with defaults based on the payload structure
            create_data = {
                'title': title
            }
            
            # Add optional string fields
            optional_string_fields = ['summary', 'step_type', 'alias', 'webhook', 'checklist_id']
            for field in optional_string_fields:
                if field in step_data and step_data[field]:
                    create_data[field] = str(step_data[field]).strip()
            
            # Add optional integer fields
            if 'position' in step_data:
                position = step_data['position']
                if isinstance(position, int) and position > 0:
                    create_data['position'] = position
                else:
                    raise ValueError("Position must be a positive integer")
            
            if 'max_assignable' in step_data:
                max_assignable = step_data['max_assignable']
                if isinstance(max_assignable, int) and max_assignable > 0:
                    create_data['max_assignable'] = max_assignable
                elif max_assignable is not None:
                    raise ValueError("max_assignable must be a positive integer or None")
            
            # Add optional boolean fields with proper string conversion
            boolean_fields = [
                'allow_guest_owners', 'skip_start_process', 'can_complete_only_assignees',
                'everyone_must_complete', 'prevent_guest_comment', 'is_soft_start_date',
                'role_changes_every_time'
            ]
            for field in boolean_fields:
                if field in step_data:
                    create_data[field] = True if step_data[field] else False
            
            # Add assignees if provided
            if 'assignees' in step_data and step_data['assignees']:
                assignees_list = step_data['assignees']
                if isinstance(assignees_list, list):
                    # Validate user IDs are integers
                    for user_id in assignees_list:
                        if not isinstance(user_id, int):
                            raise ValueError(f"User ID {user_id} must be an integer")
                    create_data['assignees'] = assignees_list
                else:
                    raise ValueError("Assignees must be a list of user IDs")
            
            # Add guests if provided
            if 'guests' in step_data and step_data['guests']:
                guests_list = step_data['guests']
                if isinstance(guests_list, list):
                    # Validate guest emails
                    import re
                    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
                    for guest_email in guests_list:
                        if not isinstance(guest_email, str) or not re.match(email_pattern, guest_email):
                            raise ValueError(f"Guest email {guest_email} is not a valid email address")
                    create_data['guests'] = guests_list
                else:
                    raise ValueError("Guests must be a list of email addresses")
            
            # Add roles if provided
            if 'roles' in step_data and step_data['roles']:
                roles_list = step_data['roles']
                if isinstance(roles_list, list):
                    create_data['roles'] = [str(role) for role in roles_list]
                else:
                    raise ValueError("Roles must be a list of role names")
            
            # Add deadline if provided (complex object)
            if 'deadline' in step_data and step_data['deadline']:
                deadline = step_data['deadline']
                if isinstance(deadline, dict):
                    deadline_data = {}
                    if 'value' in deadline:
                        deadline_data['value'] = int(deadline['value'])
                    if 'unit' in deadline:
                        valid_units = ['minutes', 'hours', 'days', 'weeks', 'months']
                        if deadline['unit'] in valid_units:
                            deadline_data['unit'] = deadline['unit']
                        else:
                            raise ValueError(f"Deadline unit must be one of: {', '.join(valid_units)}")
                    if 'option' in deadline:
                        valid_options = ['from', 'prior_to']
                        if deadline['option'] in valid_options:
                            deadline_data['option'] = deadline['option']
                        else:
                            raise ValueError(f"Deadline option must be one of: {', '.join(valid_options)}")
                    if 'step' in deadline:
                        deadline_data['step'] = deadline['step']
                    
                    if deadline_data:
                        create_data['deadline'] = deadline_data
                else:
                    raise ValueError("Deadline must be a dictionary with value, unit, option, and step")
            
            # Add start_date if provided (similar structure to deadline)
            if 'start_date' in step_data and step_data['start_date']:
                start_date = step_data['start_date']
                if isinstance(start_date, dict):
                    start_date_data = {}
                    if 'value' in start_date:
                        start_date_data['value'] = int(start_date['value'])
                    if 'unit' in start_date:
                        valid_units = ['minutes', 'hours', 'days', 'weeks', 'months']
                        if start_date['unit'] in valid_units:
                            start_date_data['unit'] = start_date['unit']
                        else:
                            raise ValueError(f"Start date unit must be one of: {', '.join(valid_units)}")
                    
                    if start_date_data:
                        create_data['start_date'] = start_date_data
                else:
                    raise ValueError("Start date must be a dictionary with value and unit")

            response_data = self.sdk._make_request('POST', endpoint, data=create_data)
            
            if isinstance(response_data, dict):
                if 'data' in response_data:
                    return response_data['data']
                return response_data
            else:
                self.sdk.logger.warning("Unexpected response format for step creation")
                return {'success': True, 'created_step': create_data}
                
        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to add step to template {template_id}: {e}")
            raise
        except ValueError as e:
            self.sdk.logger.error(f"Invalid step data: {e}")
            raise TallyfyError(f"Invalid step data: {e}")