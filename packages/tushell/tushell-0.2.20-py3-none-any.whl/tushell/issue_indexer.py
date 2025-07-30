#!/usr/bin/env python
"""
Context-Aware Indexing System for GitHub Issues
----------------------------------------------
This module implements the context-aware indexing system for GitHub issues
as specified in issue #10. It links issues to project milestones and discussion themes,
maintains relational context across discussions, and prevents stagnation.

The system provides functions to load issues, extract discussion themes and resolution patterns,
track delayed resolution, and perform other context-aware indexing operations.
"""

import os
import json
import datetime
import glob
from collections import defaultdict, Counter
from typing import Dict, List, Any, Optional, Set, Tuple

class ContextAwareIssueIndexer:
    """
    Main class for the Context-Aware Issue Indexing system.
    
    This class implements the functionality described in issue #10, including
    loading issues, extracting themes and patterns, and creating an indexed 
    representation with relational context.
    """
    
    def __init__(self, issues_dir: str = None):
        """Initialize the indexer with the directory containing issue JSON files."""
        self.issues_dir = issues_dir or os.path.join(os.getcwd(), '.mia', 'issues_cached')
        self.issues = {}
        self.indexed_issues = {}
        self.discussion_themes = defaultdict(set)
        self.resolution_patterns = {}
        self.delayed_resolutions = {}
        self.contradiction_flags = {}
        self.missing_links = []
        self.creativity_phases = {}
        self.discussion_evolution = {}
        
    def load_issues(self, directory: Optional[str] = None) -> Dict[str, Any]:
        """
        Load issues from JSON files in the specified directory.
        
        Args:
            directory: Optional path to issues directory. If None, uses the default.
            
        Returns:
            Dict mapping issue IDs to issue data.
        """
        if directory:
            self.issues_dir = directory
            
        issue_files = glob.glob(os.path.join(self.issues_dir, '*.json'))
        
        for issue_file in issue_files:
            try:
                with open(issue_file, 'r') as f:
                    issue_id = os.path.basename(issue_file).split('.')[0]
                    issue_data = json.load(f)
                    self.issues[issue_id] = issue_data
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading issue from {issue_file}: {e}")
        
        print(f"✅ Loaded {len(self.issues)} issues from {self.issues_dir}")
        return self.issues
    
    def extract_discussion_themes(self) -> Dict[str, Set[str]]:
        """
        Identify and extract themes from issue discussions.
        
        This analyzes issue titles, bodies and comments to identify common themes
        and categorize issues accordingly.
        
        Returns:
            Dict mapping theme names to sets of issue IDs.
        """
        if not self.issues:
            print("⚠️ No issues loaded. Call load_issues() first.")
            return {}
            
        # Extract keywords and themes from titles and bodies
        for issue_id, issue_data in self.issues.items():
            # Process title
            title = issue_data.get('title', '')
            if title:
                self._extract_themes_from_text(title, issue_id, weight=2)
                
            # Process body
            body = issue_data.get('body', '')
            if body:
                self._extract_themes_from_text(body, issue_id)
                
            # Process comments
            comments = issue_data.get('comments', [])
            for comment in comments:
                comment_body = comment.get('body', '')
                if comment_body:
                    self._extract_themes_from_text(comment_body, issue_id, weight=0.5)
        
        print(f"🧩 Extracted {len(self.discussion_themes)} themes across {len(self.issues)} issues")
        return self.discussion_themes
    
    def _extract_themes_from_text(self, text: str, issue_id: str, weight: float = 1.0):
        """
        Extract themes from text using keyword analysis.
        
        Args:
            text: The text to analyze
            issue_id: The ID of the issue being analyzed
            weight: Importance weight of this text (title > body > comments)
        """
        # Simple keyword-based theme extraction
        # In a production system, this would use NLP for better theme extraction
        keywords = {
            "bug": "bugs-and-fixes",
            "feature": "feature-requests", 
            "enhancement": "enhancements",
            "documentation": "docs",
            "question": "questions",
            "help": "help-requests",
            "performance": "performance",
            "security": "security",
            "UX": "user-experience",
            "UI": "user-interface",
            "test": "testing",
            "API": "api-related",
            "refactor": "refactoring",
            "recursion": "recursive-patterns",
            "echo": "echo-systems",
            "memory": "memory-management",
            "redstone": "redstone-ecosystem",
            "CLI": "command-line",
            "mia": "mia-related",
            "miette": "miette-related",
            "jeremy": "jeremy-related",
            "trinity": "trinity-embodiments"
        }
        
        text_lower = text.lower()
        for keyword, theme in keywords.items():
            if keyword.lower() in text_lower:
                self.discussion_themes[theme].add(issue_id)
    
    def extract_resolution_patterns(self) -> Dict[str, str]:
        """
        Identify and extract resolution patterns from issues.
        
        This looks for patterns in how issues are resolved, such as common
        solution approaches, time-to-resolution, and resolution quality.
        
        Returns:
            Dict mapping issue IDs to identified resolution patterns.
        """
        if not self.issues:
            print("⚠️ No issues loaded. Call load_issues() first.")
            return {}
            
        for issue_id, issue_data in self.issues.items():
            # Check for resolution in comments
            comments = issue_data.get('comments', [])
            if comments:
                # Look for resolution indicators in the last few comments
                last_comments = comments[-3:] if len(comments) >= 3 else comments
                resolution_type = self._detect_resolution_type(last_comments, issue_data)
                self.resolution_patterns[issue_id] = resolution_type
            else:
                self.resolution_patterns[issue_id] = "unresolved"
        
        # Count different resolution types
        resolution_counts = Counter(self.resolution_patterns.values())
        print(f"🔄 Extracted resolution patterns: {dict(resolution_counts)}")
        
        return self.resolution_patterns
    
    def _detect_resolution_type(self, comments: List[Dict], issue_data: Dict) -> str:
        """
        Detect the resolution type of an issue based on comments.
        
        Args:
            comments: List of comment data
            issue_data: The full issue data
            
        Returns:
            Resolution type string
        """
        # Check for common resolution keywords
        resolution_keywords = {
            "fixed": ["fixed", "resolved", "closed", "implemented", "merged", "completed"],
            "wontfix": ["won't fix", "wontfix", "not fixing", "closing as won't fix"],
            "duplicate": ["duplicate", "duplicated", "already reported"],
            "needs-info": ["need more information", "needs info", "cannot reproduce"],
            "deferred": ["defer", "deferred", "postponed", "later release"],
            "rejected": ["rejected", "declined", "not implementing"]
        }
        
        # Check for resolution keywords in comments
        for comment in comments:
            body = comment.get('body', '').lower()
            for resolution, keywords in resolution_keywords.items():
                if any(keyword in body for keyword in keywords):
                    return resolution
        
        # Check for resolution in labels
        labels = issue_data.get('labels', [])
        for label in labels:
            label_name = label.get('name', '').lower() if isinstance(label, dict) else str(label).lower()
            for resolution, keywords in resolution_keywords.items():
                if any(keyword in label_name for keyword in keywords):
                    return resolution
        
        return "unknown"
    
    def track_delayed_resolution(self) -> Dict[str, Any]:
        """
        Track issues with delayed resolutions.
        
        Identifies issues that have remained open longer than expected based on
        their category, complexity, and other factors.
        
        Returns:
            Dict mapping issue IDs to delay information.
        """
        if not self.issues:
            print("⚠️ No issues loaded. Call load_issues() first.")
            return {}
            
        # Delay thresholds in days for different themes
        delay_thresholds = {
            "bugs-and-fixes": 7,
            "feature-requests": 30,
            "enhancements": 30,
            "docs": 14,
            "questions": 3,
            "help-requests": 3,
            "performance": 14,
            "security": 5,  # Security issues should be addressed quickly
            "user-experience": 21,
            "user-interface": 21,
            "testing": 14,
            "api-related": 21,
            "refactoring": 30,
            "recursive-patterns": 30,
            "echo-systems": 30,
            "memory-management": 21,
            "redstone-ecosystem": 30,
            "command-line": 14,
            "default": 21  # Default threshold for uncategorized issues
        }
        
        # Get current date for comparison (in a real system, this would use GitHub's updated_at)
        current_date = datetime.datetime.now()
        
        for issue_id, issue_data in self.issues.items():
            # Skip if issue is already resolved
            if self.resolution_patterns.get(issue_id) in ["fixed", "wontfix", "duplicate", "rejected"]:
                continue
                
            # Find applicable theme with lowest delay threshold
            applicable_themes = []
            for theme, issues in self.discussion_themes.items():
                if issue_id in issues:
                    applicable_themes.append(theme)
            
            # Get the lowest threshold of all applicable themes, or use default
            if applicable_themes:
                threshold = min(delay_thresholds.get(theme, delay_thresholds["default"]) 
                               for theme in applicable_themes)
            else:
                threshold = delay_thresholds["default"]
                
            # For demo purposes, we'll use a random date in the past
            # In a real system, this would use the issue creation date
            # Let's simulate this with the issue ID as a seed
            days_old = int(issue_id) % 100  # Just for simulation
            
            if days_old > threshold:
                self.delayed_resolutions[issue_id] = {
                    "days_old": days_old,
                    "threshold": threshold,
                    "days_overdue": days_old - threshold,
                    "applicable_themes": applicable_themes
                }
        
        print(f"⏱️ Found {len(self.delayed_resolutions)} issues with delayed resolution")
        return self.delayed_resolutions
    
    def context_aware_indexing(self) -> Dict[str, Any]:
        """
        Create an indexed representation of issues with context awareness.
        
        This function integrates discussion themes, resolution patterns, and
        delayed resolution tracking into a comprehensive indexed representation.
        
        Returns:
            Dict representing the indexed issues with contextual relationships.
        """
        if not self.issues:
            print("⚠️ No issues loaded. Call load_issues() first.")
            return {}
        
        # Initialize the context-aware index
        self.indexed_issues = {}
        
        # Build the context-aware index for each issue
        for issue_id, issue_data in self.issues.items():
            # Extract basic issue information
            title = issue_data.get('title', 'Untitled Issue')
            body = issue_data.get('body', '')
            comments = issue_data.get('comments', [])
            
            # Build context-aware index entry
            self.indexed_issues[issue_id] = {
                "title": title,
                "body_summary": body[:200] + "..." if len(body) > 200 else body,
                "themes": [theme for theme, issues in self.discussion_themes.items() 
                          if issue_id in issues],
                "resolution_status": self.resolution_patterns.get(issue_id, "unknown"),
                "delayed": issue_id in self.delayed_resolutions,
                "delay_info": self.delayed_resolutions.get(issue_id, {}),
                "comment_count": len(comments),
                "related_issues": []  # Will be populated in the next step
            }
            
        # Build relationship network between issues based on shared themes
        self._build_relationship_network()
        
        print(f"🔍 Created context-aware index for {len(self.indexed_issues)} issues")
        return self.indexed_issues
    
    def _build_relationship_network(self):
        """Build a network of relationships between issues based on shared themes."""
        # Create a map of themes to issues
        theme_to_issues = defaultdict(set)
        for theme, issues in self.discussion_themes.items():
            theme_to_issues[theme].update(issues)
            
        # Find related issues based on shared themes
        for issue_id, issue_data in self.indexed_issues.items():
            themes = issue_data.get("themes", [])
            related = set()
            for theme in themes:
                # Add issues that share this theme, excluding the current issue
                for related_id in theme_to_issues.get(theme, set()):
                    if related_id != issue_id:
                        related.add(related_id)
            
            # Add related issues to the indexed entry
            self.indexed_issues[issue_id]["related_issues"] = list(related)
            
            # Add a relationship strength metric (# of shared themes)
            relationship_strength = {}
            for related_id in related:
                related_themes = self.indexed_issues[related_id]["themes"]
                shared_themes = set(themes) & set(related_themes)
                relationship_strength[related_id] = len(shared_themes)
            
            self.indexed_issues[issue_id]["relationship_strength"] = relationship_strength
    
    def define_desired_outcome(self) -> Dict[str, str]:
        """
        Define the desired outcome for each indexed issue.
        
        Analyzes the issue content and context to determine what an ideal
        resolution would look like.
        
        Returns:
            Dict mapping issue IDs to desired outcomes.
        """
        outcomes = {}
        
        # Outcome templates by theme
        outcome_templates = {
            "bugs-and-fixes": "Fix the bug by addressing {issue} while maintaining compatibility",
            "feature-requests": "Implement the requested feature with attention to {focus}",
            "enhancements": "Enhance the existing functionality by improving {aspect}",
            "docs": "Improve documentation for {topic} with clearer examples",
            "questions": "Provide a comprehensive answer that addresses {concern}",
            "help-requests": "Offer assistance with {problem} and document the solution",
            "performance": "Optimize {component} for better performance metrics",
            "security": "Address security vulnerability in {area} without compromising functionality",
            "user-experience": "Improve the user experience for {feature} workflow",
            "user-interface": "Enhance the interface elements for better {interaction}",
            "testing": "Create comprehensive tests for {functionality}",
            "api-related": "Refine the API to better handle {scenario}",
            "refactoring": "Refactor {code} for improved maintainability",
            "recursive-patterns": "Implement recursive pattern to handle {context} more elegantly",
            "echo-systems": "Enhance echo system to better capture {dynamic}",
            "memory-management": "Optimize memory usage for {operation}",
            "redstone-ecosystem": "Integrate {feature} with the redstone ecosystem",
            "default": "Resolve this issue by addressing the core concerns"
        }
        
        # Generate outcomes based on issue content and themes
        for issue_id, indexed_issue in self.indexed_issues.items():
            issue_data = self.issues.get(issue_id, {})
            title = issue_data.get('title', '')
            themes = indexed_issue.get('themes', [])
            
            if not themes:
                outcomes[issue_id] = outcome_templates["default"]
                continue
                
            # Pick most relevant theme (we could be more sophisticated here)
            primary_theme = themes[0]
            template = outcome_templates.get(primary_theme, outcome_templates["default"])
            
            # Extract key words from title for template filling
            # In a real system, this would use NLP to extract meaningful entities
            words = title.split()
            key_aspect = ' '.join(words[:3]) if len(words) > 3 else title
            
            # Fill in the template
            filled_template = template.format(
                issue=key_aspect,
                focus=key_aspect,
                aspect=key_aspect,
                topic=key_aspect,
                concern=key_aspect,
                problem=key_aspect,
                component=key_aspect,
                area=key_aspect,
                feature=key_aspect,
                interaction=key_aspect,
                functionality=key_aspect,
                scenario=key_aspect,
                code=key_aspect,
                context=key_aspect,
                dynamic=key_aspect,
                operation=key_aspect
            )
            
            outcomes[issue_id] = filled_template
            # Update the indexed issue
            self.indexed_issues[issue_id]["desired_outcome"] = filled_template
            
        print(f"🎯 Defined desired outcomes for {len(outcomes)} issues")
        return outcomes
    
    def define_current_reality(self) -> Dict[str, str]:
        """
        Define the current reality for each indexed issue.
        
        Analyzes the current state of the issue based on its description,
        comments, and other contextual information.
        
        Returns:
            Dict mapping issue IDs to current reality descriptions.
        """
        realities = {}
        
        for issue_id, indexed_issue in self.indexed_issues.items():
            issue_data = self.issues.get(issue_id, {})
            resolution_status = indexed_issue.get('resolution_status', 'unknown')
            
            # Base reality on resolution status
            if resolution_status == 'fixed':
                reality = "This issue has been resolved. The implementation is complete."
            elif resolution_status == 'wontfix':
                reality = "This issue will not be addressed due to constraints or priorities."
            elif resolution_status == 'duplicate':
                reality = "This issue is a duplicate of another existing issue."
            elif resolution_status == 'needs-info':
                reality = "More information is needed to properly address this issue."
            elif resolution_status == 'deferred':
                reality = "This issue has been deferred to a future release or milestone."
            elif resolution_status == 'rejected':
                reality = "This issue has been rejected and will not be implemented."
            else:
                # Default for unresolved issues
                if indexed_issue.get('delayed', False):
                    delay_info = indexed_issue.get('delay_info', {})
                    days_overdue = delay_info.get('days_overdue', 0)
                    reality = f"This issue is still open and has been delayed by {days_overdue} days beyond the expected timeline."
                else:
                    reality = "This issue is still open and under consideration."
            
            realities[issue_id] = reality
            # Update the indexed issue
            self.indexed_issues[issue_id]["current_reality"] = reality
            
        print(f"📊 Defined current reality for {len(realities)} issues")
        return realities
    
    def define_action_steps(self) -> Dict[str, List[str]]:
        """
        Define the action steps for each indexed issue.
        
        Based on the gap between current reality and desired outcome,
        this function suggests concrete steps to resolve each issue.
        
        Returns:
            Dict mapping issue IDs to lists of action steps.
        """
        action_steps = {}
        
        for issue_id, indexed_issue in self.indexed_issues.items():
            steps = []
            resolution_status = indexed_issue.get('resolution_status', 'unknown')
            themes = indexed_issue.get('themes', [])
            
            # Skip issues that are already resolved or won't be fixed
            if resolution_status in ['fixed', 'wontfix', 'duplicate', 'rejected']:
                action_steps[issue_id] = ["No action needed - issue is already resolved or won't be fixed."]
                continue
            
            # Add step to gather more info if needed
            if resolution_status == 'needs-info':
                steps.append("Request additional information from the issue reporter.")
                
            # Generic steps based on issue themes
            for theme in themes:
                if theme == "bugs-and-fixes":
                    steps.append("Reproduce the issue in a controlled environment.")
                    steps.append("Identify the root cause of the bug.")
                    steps.append("Implement a fix with appropriate test coverage.")
                    steps.append("Verify the fix resolves the issue without introducing regressions.")
                elif theme == "feature-requests" or theme == "enhancements":
                    steps.append("Create a detailed design specification.")
                    steps.append("Get feedback on the design from stakeholders.")
                    steps.append("Implement the feature with tests.")
                    steps.append("Update documentation to cover the new functionality.")
                elif theme == "performance":
                    steps.append("Profile the code to identify performance bottlenecks.")
                    steps.append("Implement optimizations for the identified bottlenecks.")
                    steps.append("Benchmark the optimized implementation.")
                elif theme == "security":
                    steps.append("Assess the security risk and impact.")
                    steps.append("Implement a security patch.")
                    steps.append("Conduct security validation testing.")
                # Add more theme-specific steps as needed
            
            # If delayed, add escalation step
            if indexed_issue.get('delayed', False):
                steps.append("Escalate this delayed issue for prioritization.")
            
            # If no specific steps were added, add a generic step
            if not steps:
                steps.append("Analyze the issue and determine appropriate actions.")
                steps.append("Implement a solution according to project standards.")
                steps.append("Add tests to verify the solution works as expected.")
                
            action_steps[issue_id] = steps
            # Update the indexed issue
            self.indexed_issues[issue_id]["action_steps"] = steps
            
        print(f"📝 Defined action steps for {len(action_steps)} issues")
        return action_steps
    
    def determine_creative_phase(self) -> Dict[str, str]:
        """
        Determine the creative phase for each indexed issue.
        
        Categorizes issues into different phases of the creative process:
        ideation, exploration, implementation, refinement, or validation.
        
        Returns:
            Dict mapping issue IDs to creative phases.
        """
        phases = {}
        
        # Phase determination heuristics
        for issue_id, indexed_issue in self.indexed_issues.items():
            issue_data = self.issues.get(issue_id, {})
            resolution_status = indexed_issue.get('resolution_status', 'unknown')
            comment_count = indexed_issue.get('comment_count', 0)
            
            # Phase determination logic
            if resolution_status in ['fixed', 'wontfix', 'duplicate', 'rejected']:
                phase = "completed"
            elif resolution_status == 'needs-info':
                phase = "ideation"
            elif comment_count == 0:
                phase = "ideation"
            elif comment_count <= 2:
                phase = "exploration"
            elif comment_count <= 5:
                phase = "implementation"
            else:
                phase = "refinement"
            
            # Additional signals for validation phase
            body = issue_data.get('body', '').lower()
            comments = issue_data.get('comments', [])
            if comments and any("test" in comment.get('body', '').lower() for comment in comments[-2:]):
                phase = "validation"
            
            phases[issue_id] = phase
            # Update the indexed issue
            self.indexed_issues[issue_id]["creative_phase"] = phase
            self.creativity_phases[issue_id] = phase
            
        # Aggregate phase statistics
        phase_counts = Counter(phases.values())
        print(f"🎨 Creative phases: {dict(phase_counts)}")
        
        return phases
    
    def capture_discussion_evolution(self) -> Dict[str, Dict]:
        """
        Capture the evolution of discussions for each indexed issue.
        
        Analyzes the comment flow to understand how discussions evolve,
        identify key turning points, and moments of insight.
        
        Returns:
            Dict mapping issue IDs to discussion evolution data.
        """
        discussion_evolution = {}
        
        for issue_id, issue_data in self.issues.items():
            comments = issue_data.get('comments', [])
            if not comments:
                discussion_evolution[issue_id] = {"evolution": "no discussion"}
                continue
                
            # Create a timeline of the discussion
            timeline = []
            
            # First point is the issue creation
            timeline.append({
                "type": "creation",
                "content": issue_data.get('body', '')[:100],
                "point": 0
            })
            
            # Add comments to the timeline
            for i, comment in enumerate(comments):
                content = comment.get('body', '')
                timeline.append({
                    "type": "comment",
                    "content": content[:100],
                    "point": i + 1
                })
            
            # Identify discussion shifts
            shifts = []
            current_theme = None
            for i, point in enumerate(timeline):
                # In a real system, we'd use NLP to identify theme shifts
                # For now, we'll just use simple heuristics
                new_theme = self._extract_primary_theme_from_text(point["content"])
                if new_theme != current_theme:
                    shifts.append({
                        "point": i,
                        "from": current_theme,
                        "to": new_theme
                    })
                    current_theme = new_theme
            
            discussion_evolution[issue_id] = {
                "timeline": timeline,
                "shifts": shifts,
                "evolution": "linear" if len(shifts) <= 1 else "complex"
            }
            
            # Update the indexed issue
            self.indexed_issues[issue_id]["discussion_evolution"] = {
                "pattern": "linear" if len(shifts) <= 1 else "complex",
                "shift_count": len(shifts)
            }
            self.discussion_evolution[issue_id] = discussion_evolution[issue_id]
            
        print(f"💬 Captured discussion evolution for {len(discussion_evolution)} issues")
        return discussion_evolution
    
    def _extract_primary_theme_from_text(self, text: str) -> str:
        """Extract the primary theme from text."""
        # This is a simplified placeholder - a real implementation would use NLP
        keywords = {
            "bug": "technical",
            "feature": "feature", 
            "enhancement": "feature",
            "documentation": "docs",
            "question": "question",
            "help": "question",
            "performance": "technical",
            "security": "technical",
            "UX": "design",
            "UI": "design",
            "test": "testing",
        }
        
        text_lower = text.lower()
        for keyword, theme in keywords.items():
            if keyword.lower() in text_lower:
                return theme
                
        return "general"
    
    def flag_contradictions(self) -> Dict[str, List[Dict]]:
        """
        Flag contradictions in the indexed issues.
        
        Identifies potential inconsistencies between issues, such as
        conflicting requirements or solutions.
        
        Returns:
            Dict mapping issue IDs to lists of contradictions.
        """
        contradictions = defaultdict(list)
        
        # Get all issue pairs with shared themes
        issue_pairs = []
        for issue_id, indexed_issue in self.indexed_issues.items():
            related_issues = indexed_issue.get('related_issues', [])
            for related_id in related_issues:
                # Ensure we don't add the same pair twice
                if (related_id, issue_id) not in issue_pairs:
                    issue_pairs.append((issue_id, related_id))
        
        # Check each pair for potential contradictions
        for issue1_id, issue2_id in issue_pairs:
            issue1 = self.issues.get(issue1_id, {})
            issue2 = self.issues.get(issue2_id, {})
            indexed1 = self.indexed_issues.get(issue1_id, {})
            indexed2 = self.indexed_issues.get(issue2_id, {})
            
            # Look for opposing resolutions
            resolution1 = indexed1.get('resolution_status', 'unknown')
            resolution2 = indexed2.get('resolution_status', 'unknown')
            
            if resolution1 == 'fixed' and resolution2 == 'wontfix' or \
               resolution1 == 'wontfix' and resolution2 == 'fixed':
                contradictions[issue1_id].append({
                    "type": "opposing_resolutions",
                    "issue_id": issue2_id,
                    "description": "This issue has an opposing resolution to a related issue."
                })
                contradictions[issue2_id].append({
                    "type": "opposing_resolutions",
                    "issue_id": issue1_id,
                    "description": "This issue has an opposing resolution to a related issue."
                })
            
            # More contradiction checks could be added here
            # For example, checking for keywords that indicate opposing approaches
            
        # Update the indexed issues with contradiction flags
        for issue_id, flags in contradictions.items():
            self.indexed_issues[issue_id]["contradictions"] = flags
            self.contradiction_flags[issue_id] = flags
            
        print(f"⚠️ Flagged contradictions in {len(contradictions)} issues")
        return dict(contradictions)
    
    def predict_missing_links(self) -> List[Dict]:
        """
        Predict missing links in the indexed issues.
        
        Identifies potential connections between issues that aren't
        explicitly linked but should be.
        
        Returns:
            List of dicts describing missing links.
        """
        missing_links = []
        
        # Build a map of themes to issues
        theme_issue_map = defaultdict(list)
        for issue_id, indexed_issue in self.indexed_issues.items():
            for theme in indexed_issue.get('themes', []):
                theme_issue_map[theme].append(issue_id)
        
        # Find issues that share multiple themes but aren't linked
        checked_pairs = set()
        for theme, issues in theme_issue_map.items():
            if len(issues) < 2:
                continue
                
            for i, issue1_id in enumerate(issues):
                for issue2_id in issues[i+1:]:
                    # Skip if already checked this pair
                    pair_key = tuple(sorted([issue1_id, issue2_id]))
                    if pair_key in checked_pairs:
                        continue
                    checked_pairs.add(pair_key)
                    
                    # Get the indexed issues
                    indexed1 = self.indexed_issues[issue1_id]
                    indexed2 = self.indexed_issues[issue2_id]
                    
                    # Check if they're already linked
                    if issue2_id in indexed1.get('related_issues', []) or \
                       issue1_id in indexed2.get('related_issues', []):
                        continue
                    
                    # Count shared themes
                    themes1 = set(indexed1.get('themes', []))
                    themes2 = set(indexed2.get('themes', []))
                    shared_themes = themes1.intersection(themes2)
                    
                    # If they share multiple themes, suggest a link
                    if len(shared_themes) >= 2:
                        missing_links.append({
                            "issue1_id": issue1_id,
                            "issue2_id": issue2_id,
                            "shared_themes": list(shared_themes),
                            "confidence": len(shared_themes) / max(len(themes1), len(themes2))
                        })
                        
        # Sort by confidence (descending)
        missing_links.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Store the missing links
        self.missing_links = missing_links
        
        print(f"🔄 Predicted {len(missing_links)} missing links")
        return missing_links
    
    def automate_issue_status_updates(self) -> Dict[str, Dict]:
        """
        Generate automated status updates for indexed issues.
        
        Creates status update suggestions based on the indexed information,
        which could be used to update the actual issues.
        
        Returns:
            Dict mapping issue IDs to status update information.
        """
        status_updates = {}
        
        for issue_id, indexed_issue in self.indexed_issues.items():
            resolution_status = indexed_issue.get('resolution_status', 'unknown')
            is_delayed = indexed_issue.get('delayed', False)
            creative_phase = indexed_issue.get('creative_phase', 'unknown')
            contradictions = indexed_issue.get('contradictions', [])
            
            # Skip resolved issues
            if resolution_status in ['fixed', 'wontfix', 'duplicate', 'rejected']:
                continue
                
            # Generate status update based on gathered information
            update = {
                "status_change": None,
                "comment": "",
                "labels_to_add": [],
                "labels_to_remove": []
            }
            
            # Add phase label
            update["labels_to_add"].append(f"phase:{creative_phase}")
            
            # Handle delayed issues
            if is_delayed:
                delay_info = indexed_issue.get('delay_info', {})
                days_overdue = delay_info.get('days_overdue', 0)
                update["comment"] += f"⚠️ This issue is delayed by {days_overdue} days. "
                update["labels_to_add"].append("delayed")
            
            # Add info about contradictions
            if contradictions:
                update["comment"] += f"⚠️ This issue may have contradictions with: "
                update["comment"] += ", ".join([c["issue_id"] for c in contradictions])
                update["comment"] += ". "
                update["labels_to_add"].append("has-contradictions")
            
            # Add next steps based on action steps
            action_steps = indexed_issue.get('action_steps', [])
            if action_steps:
                update["comment"] += "\n\n**Suggested Next Steps:**\n"
                for i, step in enumerate(action_steps[:3]):  # Show top 3 steps
                    update["comment"] += f"{i+1}. {step}\n"
            
            # Only include meaningful updates
            if update["comment"] or update["labels_to_add"] or update["labels_to_remove"]:
                status_updates[issue_id] = update
        
        print(f"📝 Generated automated status updates for {len(status_updates)} issues")
        return status_updates
    
    def save_indexed_issues(self, output_file: str = None) -> str:
        """
        Save the indexed issues to a file.
        
        Args:
            output_file: Path to the output file. If None, a default is used.
            
        Returns:
            Path to the saved file.
        """
        if not output_file:
            output_dir = os.path.join(os.getcwd(), '.mia')
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(output_dir, f"indexed_issues_{timestamp}.json")
        
        # Create output data structure
        output_data = {
            "metadata": {
                "indexed_at": datetime.datetime.now().isoformat(),
                "issue_count": len(self.indexed_issues),
                "theme_count": len(self.discussion_themes)
            },
            "indexed_issues": self.indexed_issues,
            "themes": {k: list(v) for k, v in self.discussion_themes.items()},
            "resolution_patterns": self.resolution_patterns,
            "delayed_resolutions": self.delayed_resolutions,
            "creativity_phases": self.creativity_phases,
            "missing_links": self.missing_links,
            "contradiction_flags": self.contradiction_flags
        }
        
        try:
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
                
            print(f"💾 Saved indexed issues to {output_file}")
            return output_file
        except IOError as e:
            print(f"Error saving indexed issues: {e}")
            return None
    
    def run_full_indexing_pipeline(self, issues_dir: Optional[str] = None) -> str:
        """
        Run the complete indexing pipeline from loading to saving.
        
        Args:
            issues_dir: Optional path to directory containing issue files.
            
        Returns:
            Path to the saved indexed issues file.
        """
        print("🚀 Starting context-aware indexing pipeline...")
        
        # Execute the indexing pipeline
        self.load_issues(issues_dir)
        self.extract_discussion_themes()
        self.extract_resolution_patterns()
        self.track_delayed_resolution()
        self.context_aware_indexing()
        self.define_desired_outcome()
        self.define_current_reality()
        self.define_action_steps()
        self.determine_creative_phase()
        self.capture_discussion_evolution()
        self.flag_contradictions()
        self.predict_missing_links()
        self.automate_issue_status_updates()
        
        # Save the results
        output_file = self.save_indexed_issues()
        
        print("✅ Context-aware indexing pipeline completed!")
        return output_file

def main():
    """Main function for testing the issue indexer."""
    indexer = ContextAwareIssueIndexer()
    output_file = indexer.run_full_indexing_pipeline()
    print(f"Indexed issues saved to {output_file}")

if __name__ == "__main__":
    main()