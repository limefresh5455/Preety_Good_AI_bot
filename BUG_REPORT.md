# Bug Report: Pretty Good AI Voice Agent Testing

**Date:** February 05, 2026 at 04:01 PM  
**Calls Analyzed:** 10  
**Total Issues Found:** 23

## Executive Summary

This report documents bugs and quality issues discovered through automated testing of the Pretty Good AI voice agent. Each call simulated a realistic patient interaction to test the agent's ability to handle common medical office scenarios.

### Severity Breakdown
- **Critical:** 0 - System failures preventing basic functionality
- **High:** 4 - Major issues affecting user experience  
- **Medium:** 0 - Noticeable problems that should be fixed
- **Low:** 17 - Minor quality improvements

---

## Critical Issues

*No critical issues found.*

---

## High Severity Issues

*These issues significantly impact the user experience and should be prioritized.*

### 1. Failed to acknowledge appointment request

**Call ID:** `CA5dbf360b102d078067ca808c45e77ead`

**Test Scenario:** Request an MRI or X-ray appointment for hip pain

**Agent's Response:**
> Training purposes.

**Why This Matters:** Agent failed to understand the core intent of the call

---

### 2. Failed to acknowledge appointment request

**Call ID:** `CA3ad079f97787f13598248d13326139ba`

**Test Scenario:** Schedule an appointment for knee pain that started after running

**Agent's Response:**
> Training purposes.

**Why This Matters:** Agent failed to understand the core intent of the call

---

### 3. Failed to acknowledge appointment request

**Call ID:** `CA9a072379448e4f5216e74a483a188aa2`

**Test Scenario:** Schedule an appointment for back pain that's been ongoing for weeks

**Agent's Response:**
> Services.

**Why This Matters:** Agent failed to understand the core intent of the call

---

### 4. Failed to acknowledge appointment request

**Call ID:** `CA1ee52fecfe9a844a64503f13968e0709`

**Test Scenario:** Reschedule a post-surgery follow-up appointment

**Agent's Response:**
> Purposes. But

**Why This Matters:** Agent failed to understand the core intent of the call

---

## Medium Severity Issues

*These issues detract from the experience but don't prevent core functionality.*

*No medium severity issues found.*

---

## Low Severity / Polish Issues

*Minor improvements that would enhance perceived quality.*

### 1. Missing proper greeting

**Call ID:** `CA3f9708811c589700085a2d36ed41f4eb`

**Example:**
> And training purposes.

---

### 2. Missing proper closing phrase

**Call ID:** `CA3f9708811c589700085a2d36ed41f4eb`

---

### 3. Missing proper greeting

**Call ID:** `CAaf4461c0e8481ac3603f7023a4a54983`

**Example:**
> Purposes.

---

### 4. Missing proper greeting

**Call ID:** `CAc848444ec7dd69b1dc3e455b54e04102`

**Example:**
> Purposes. But

---

### 5. Missing proper closing phrase

**Call ID:** `CAc848444ec7dd69b1dc3e455b54e04102`

---

### 6. Missing proper greeting

**Call ID:** `CA5dbf360b102d078067ca808c45e77ead`

**Example:**
> Training purposes.

---

### 7. Missing proper closing phrase

**Call ID:** `CA5dbf360b102d078067ca808c45e77ead`

---

### 8. Missing proper closing phrase

**Call ID:** `CA2c1882cfb4b271431a24194b28228395`

---

### 9. Missing proper greeting

**Call ID:** `CA3ad079f97787f13598248d13326139ba`

**Example:**
> Training purposes.

---

### 10. Missing proper closing phrase

**Call ID:** `CA3ad079f97787f13598248d13326139ba`

---

### 11. Missing proper greeting

**Call ID:** `CA9a072379448e4f5216e74a483a188aa2`

**Example:**
> Services.

---

### 12. Missing proper closing phrase

**Call ID:** `CA9a072379448e4f5216e74a483a188aa2`

---

### 13. Missing proper greeting

**Call ID:** `CA1ee52fecfe9a844a64503f13968e0709`

**Example:**
> Purposes. But

---

### 14. Missing proper closing phrase

**Call ID:** `CA1ee52fecfe9a844a64503f13968e0709`

---

### 15. Missing proper greeting

**Call ID:** `CAc84ee1991f7664f186c519a3229f23f1`

**Example:**
> Purposes.

---

### 16. Missing proper closing phrase

**Call ID:** `CAc84ee1991f7664f186c519a3229f23f1`

---

### 17. Missing proper greeting

**Call ID:** `CAaf4461c0e8481ac3603f7023a4a54983`

**Example:**
> Purposes.

---

## Common Patterns

*Issues that appeared multiple times across different calls.*

| Issue Type | Occurrences |
|-----------|-------------|
| Agent expressed uncertainty | 2 |

---

## Recommendations

1. **Improve Intent Recognition**: Agent needs better training on recognizing appointment and prescription requests in the opening statement

2. **Standardize Greetings**: Ensure all calls start with a polite, professional greeting

3. **Add Closing Protocol**: Implement proper conversation endings with thank you and goodbye

---

## Test Data

All 10 call transcripts are available in the `transcripts/` directory.

Each transcript includes:
- Full conversation history
- Timing information
- Real-time issue detection
- Call metadata
