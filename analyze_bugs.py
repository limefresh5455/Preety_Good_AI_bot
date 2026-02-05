import json
import os
from datetime import datetime
from collections import Counter, defaultdict


class BugAnalyzer:
    """Analyzes transcripts to find bugs and quality issues"""
    
    def __init__(self, transcripts_dir="transcripts"):
        self.transcripts_dir = transcripts_dir
        self.transcripts = []
        self.all_issues = []
        
    def load_transcripts(self):
        """Load all transcript JSON files"""
        if not os.path.exists(self.transcripts_dir):
            print(f"No transcripts found at {self.transcripts_dir}")
            return
        
        files = [f for f in os.listdir(self.transcripts_dir) 
                 if f.endswith('.json')]
        
        for filename in files:
            filepath = os.path.join(self.transcripts_dir, filename)
            with open(filepath, 'r') as f:
                self.transcripts.append(json.load(f))
        
        print(f"Loaded {len(self.transcripts)} transcripts")
    
    def analyze_transcripts(self):
        """Run detailed analysis on all transcripts"""
        bugs = []
        
        for t in self.transcripts:
            messages = t.get('messages', [])
            scenario = t.get('scenario', '')
            call_sid = t['call_sid']
            
            agent_msgs = [m['text'] for m in messages if m['speaker'] == 'Agent']
            patient_msgs = [m['text'] for m in messages if m['speaker'] == 'Patient']
            
            if not agent_msgs:
                bugs.append({
                    'call_sid': call_sid,
                    'type': 'critical',
                    'issue': 'No agent response received',
                    'scenario': scenario
                })
                continue

            first_agent = agent_msgs[0] if agent_msgs else ""
            
            if any(word in scenario.lower() for word in ['schedule', 'appointment', 'reschedule']):
                if not any(word in first_agent.lower() for word in ['appointment', 'schedule']):
                    bugs.append({
                        'call_sid': call_sid,
                        'type': 'high',
                        'issue': 'Failed to acknowledge appointment request',
                        'scenario': scenario,
                        'agent_response': first_agent[:200]
                    })
            
            if 'refill' in scenario.lower() or 'prescription' in scenario.lower():
                if not any(word in first_agent.lower() for word in ['prescription', 'refill', 'medication']):
                    bugs.append({
                        'call_sid': call_sid,
                        'type': 'high',
                        'issue': 'Failed to acknowledge prescription refill request',
                        'scenario': scenario,
                        'agent_response': first_agent[:200]
                    })

            for i in range(len(agent_msgs) - 1):
                if agent_msgs[i] == agent_msgs[i+1]:
                    bugs.append({
                        'call_sid': call_sid,
                        'type': 'medium',
                        'issue': 'Agent repeated exact same response',
                        'example': agent_msgs[i][:200]
                    })

            if len(messages) < 4:
                bugs.append({
                    'call_sid': call_sid,
                    'type': 'medium',
                    'issue': 'Conversation ended prematurely',
                    'turns': len(messages) // 2
                })

            if first_agent:
                has_greeting = any(word in first_agent.lower() 
                                 for word in ['hello', 'hi', 'good', 'thank'])
                if not has_greeting:
                    bugs.append({
                        'call_sid': call_sid,
                        'type': 'low',
                        'issue': 'Missing proper greeting',
                        'example': first_agent[:150]
                    })

            if messages:
                last_msg = messages[-1]['text'].lower()
                has_closing = any(word in last_msg 
                                for word in ['goodbye', 'bye', 'thank you'])
                if not has_closing:
                    bugs.append({
                        'call_sid': call_sid,
                        'type': 'low',
                        'issue': 'Missing proper closing phrase'
                    })

            self.all_issues.extend(t.get('issues', []))
        
        return bugs
    
    def generate_report(self, output_file="BUG_REPORT.md"):
        """Generate comprehensive bug report"""
        self.load_transcripts()
        bugs = self.analyze_transcripts()
        
        critical = [b for b in bugs if b['type'] == 'critical']
        high = [b for b in bugs if b['type'] == 'high']
        medium = [b for b in bugs if b['type'] == 'medium']
        low = [b for b in bugs if b['type'] == 'low']
        
        issue_counts = Counter(self.all_issues)
        
        report = f"""# Bug Report: Pretty Good AI Voice Agent Testing

**Date:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}  
**Calls Analyzed:** {len(self.transcripts)}  
**Total Issues Found:** {len(bugs) + len(self.all_issues)}

## Executive Summary

This report documents bugs and quality issues discovered through automated testing of the Pretty Good AI voice agent. Each call simulated a realistic patient interaction to test the agent's ability to handle common medical office scenarios.

### Severity Breakdown
- **Critical:** {len(critical)} - System failures preventing basic functionality
- **High:** {len(high)} - Major issues affecting user experience  
- **Medium:** {len(medium)} - Noticeable problems that should be fixed
- **Low:** {len(low)} - Minor quality improvements

---

## Critical Issues

"""
        
        if critical:
            for i, bug in enumerate(critical, 1):
                report += f"### {i}. {bug['issue']}\n\n"
                report += f"**Call ID:** `{bug['call_sid']}`\n\n"
                if 'scenario' in bug:
                    report += f"**Scenario:** {bug['scenario']}\n\n"
                report += "**Impact:** Agent completely failed to respond\n\n"
                report += "---\n\n"
        else:
            report += "*No critical issues found.*\n\n---\n\n"
        
        report += "## High Severity Issues\n\n"
        report += "*These issues significantly impact the user experience and should be prioritized.*\n\n"
        
        if high:
            for i, bug in enumerate(high, 1):
                report += f"### {i}. {bug['issue']}\n\n"
                report += f"**Call ID:** `{bug['call_sid']}`\n\n"
                if 'scenario' in bug:
                    report += f"**Test Scenario:** {bug['scenario']}\n\n"
                if 'agent_response' in bug:
                    report += "**Agent's Response:**\n"
                    report += f"> {bug['agent_response']}\n\n"
                report += "**Why This Matters:** Agent failed to understand the core intent of the call\n\n"
                report += "---\n\n"
        else:
            report += "*No high severity issues found.*\n\n---\n\n"
        
        report += "## Medium Severity Issues\n\n"
        report += "*These issues detract from the experience but don't prevent core functionality.*\n\n"
        
        if medium:
            for i, bug in enumerate(medium, 1):
                report += f"### {i}. {bug['issue']}\n\n"
                report += f"**Call ID:** `{bug['call_sid']}`\n\n"
                if 'example' in bug:
                    report += "**Example:**\n"
                    report += f"> {bug['example']}\n\n"
                if 'turns' in bug:
                    report += f"**Conversation Length:** Only {bug['turns']} turns\n\n"
                report += "---\n\n"
        else:
            report += "*No medium severity issues found.*\n\n---\n\n"
        
        report += "## Low Severity / Polish Issues\n\n"
        report += "*Minor improvements that would enhance perceived quality.*\n\n"
        
        if low:
            for i, bug in enumerate(low, 1):
                report += f"### {i}. {bug['issue']}\n\n"
                report += f"**Call ID:** `{bug['call_sid']}`\n\n"
                if 'example' in bug:
                    report += "**Example:**\n"
                    report += f"> {bug['example']}\n\n"
                report += "---\n\n"
        else:
            report += "*No low severity issues found.*\n\n---\n\n"
        
        report += "## Common Patterns\n\n"
        report += "*Issues that appeared multiple times across different calls.*\n\n"
        
        if issue_counts:
            report += "| Issue Type | Occurrences |\n"
            report += "|-----------|-------------|\n"
            for issue, count in issue_counts.most_common():
                report += f"| {issue} | {count} |\n"
            report += "\n"
        else:
            report += "*No recurring patterns detected.*\n\n"
        
        report += "---\n\n"
        report += "## Recommendations\n\n"
        
        recs = []
        
        if any('acknowledge' in b['issue'].lower() for b in bugs):
            recs.append("**Improve Intent Recognition**: Agent needs better training on recognizing appointment and prescription requests in the opening statement")
        
        if any('repeated' in b['issue'].lower() for b in bugs):
            recs.append("**Fix Response Loop**: Implement conversation state tracking to prevent repeating the same response")
        
        if any('greeting' in b['issue'].lower() for b in bugs):
            recs.append("**Standardize Greetings**: Ensure all calls start with a polite, professional greeting")
        
        if any('closing' in b['issue'].lower() for b in bugs):
            recs.append("**Add Closing Protocol**: Implement proper conversation endings with thank you and goodbye")
        
        if any('prematurely' in b['issue'].lower() for b in bugs):
            recs.append("**Extend Conversations**: Agent should ask follow-up questions rather than ending calls abruptly")
        
        if recs:
            for j, rec in enumerate(recs, 1):
                report += f"{j}. {rec}\n\n"
        else:
            report += "*Overall performance is good. Continue monitoring for edge cases.*\n\n"
        
        report += "---\n\n"
        report += "## Test Data\n\n"
        report += f"All {len(self.transcripts)} call transcripts are available in the `transcripts/` directory.\n\n"
        report += "Each transcript includes:\n"
        report += "- Full conversation history\n"
        report += "- Timing information\n"
        report += "- Real-time issue detection\n"
        report += "- Call metadata\n"
        
        # Save report
        with open(output_file, 'w') as f:
            f.write(report)
        
        print(f"\n{'='*60}")
        print(f"Bug report generated: {output_file}")
        print(f"Total issues: {len(bugs) + len(self.all_issues)}")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    analyzer = BugAnalyzer()
    analyzer.generate_report()
