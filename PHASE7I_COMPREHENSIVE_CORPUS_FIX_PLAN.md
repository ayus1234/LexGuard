# Phase 7I: Comprehensive Corpus Integrity Fix - CRITICAL

**Date**: 2026-09-26  
**Status**: ⚠️ CRITICAL ISSUES IDENTIFIED - MUST FIX BEFORE SUBMISSION  
**Previous Phase**: 7H (Incomplete/Buggy)  

---

## CRITICAL ISSUES IDENTIFIED BY USER

### Issue 1: Fake Category Counts
**Problem**: All categories show "62" regardless of actual data  
**Root Cause**: Line 58 in library/page.tsx: `return Math.floor(stats.total_count / 8);` → 500/8 = 62  
**Impact**: Completely fake data, obvious to evaluators  

### Issue 2: Wrong Categories for Different Scopes
**Problem**: Templates categories (Technology & SaaS, Employment, etc.) shown for Public Laws and Demo Docs  
**Root Cause**: `sampleCategories` array is static and doesn't change based on `selectedDocType`  
**Impact**: Public Laws should show "Corporate Governance", "Commercial Code", etc., NOT "Technology & SaaS"  

### Issue 3: Category Pills Don't Match Scope
**Problem**: Switching from Templates → Public Laws → Demo Docs keeps showing the same category pills  
**Root Cause**: Categories are computed once from stats, not dynamically per scope  
**Impact**: UI claims to switch scopes but doesn't actually change the category structure  

### Issue 4: Pagination Shows "1-6 of 6"
**Problem**: Despite backend returning 200 documents, UI shows only 6  
**Root Cause**: Need to verify if frontend is actually deployed with Phase 7H changes  
**Impact**: Complete data mismatch visible to user  

---

## ROOT CAUSE ANALYSIS

### Backend Corpus Structure (CORRECT):
```python
# backend/app/core/corpus.py

TEMPLATES (200):
- Technology & SaaS: 34
- Employment & HR: 28
- NDA & Confidentiality: 22
- Business & Corporate: 31
- Intellectual Property: 19
- Property & Real Estate: 26
- Finance & Lending: 24
- Privacy & Data: 16

PUBLIC_LAWS (285):
- Corporate Governance & Formation
- Commercial Code & Contracts (UCC)
- Intellectual Property & Trade Secrets
- Labor & Employment Standards
- Privacy & Data Protection
- Dispute Resolution & Arbitration
(6 categories distributed across federal, state statutes)

DEMO_DOCUMENTS (15):
- Technology & SaaS: 3 (doc-saas-v42, doc-sla-addendum, doc-software-license)
- NDA & Confidentiality: 1 (doc-nda-bilateral)
- Employment & HR: 1 (doc-exec-employment)
- Property & Real Estate: 2 (doc-cre-nnn, doc-commercial-lease)
- Finance & Lending: 2 (doc-series-a-term, doc-loan-security)
- Privacy & Data: 1 (doc-dpa-gdpr)
- Business & Corporate: 4 (doc-vendor-services, doc-joint-venture, doc-settlement-release, doc-asset-purchase)
- Intellectual Property: 1 (doc-ip-assignment)
```

### Frontend Implementation (WRONG):
- Uses fake `Math.floor(stats.total_count / 8)` for all categories → 62
- Shows template categories for ALL scopes
- Doesn't dynamically compute categories per scope
- May not be properly deployed

---

## COMPREHENSIVE FIX REQUIRED

### 1. Backend Enhancement: Add Category Counts Endpoint

**New Endpoint**: `GET /api/v1/corpus/categories?doc_type=template`

**Purpose**: Return actual category counts for the selected scope

**Response**:
```json
{
  "doc_type": "template",
  "categories": [
    {"name": "Technology & SaaS", "count": 34},
    {"name": "Employment & HR", "count": 28},
    {"name": "NDA & Confidentiality", "count": 22},
    {"name": "Business & Corporate", "count": 31},
    {"name": "Intellectual Property", "count": 19},
    {"name": "Property & Real Estate", "count": 26},
    {"name": "Finance & Lending", "count": 24},
    {"name": "Privacy & Data", "count": 16}
  ]
}
```

For public_law:
```json
{
  "doc_type": "public_law",
  "categories": [
    {"name": "Corporate Governance & Formation", "count": 48},
    {"name": "Commercial Code & Contracts (UCC)", "count": 48},
    {"name": "Intellectual Property & Trade Secrets", "count": 48},
    {"name": "Labor & Employment Standards", "count": 47},
    {"name": "Privacy & Data Protection", "count": 47},
    {"name": "Dispute Resolution & Arbitration", "count": 47}
  ]
}
```

**Implementation**:
```python
# backend/app/api/routes/corpus.py

@router.get("/categories")
async def get_corpus_categories(
    doc_type: Optional[str] = Query(None)
) -> Dict[str, Any]:
    """Get category counts for a specific document type."""
    docs = corpus_registry.filter(doc_type=doc_type) if doc_type else corpus_registry.list_all()
    
    # Count by category
    category_counts: Dict[str, int] = {}
    for doc in docs:
        category_counts[doc.category] = category_counts.get(doc.category, 0) + 1
    
    # Sort by count descending
    sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "doc_type": doc_type or "all",
        "categories": [{"name": name, "count": count} for name, count in sorted_categories]
    }
```

### 2. Frontend Fix: Dynamic Categories Per Scope

**Changes to `src/app/library/page.tsx`**:

```typescript
// Add state for scope-specific categories
const [scopeCategories, setScopeCategories] = useState<Array<{name: string; count: number; id: string}>>([]);

// Fetch categories whenever scope changes
useEffect(() => {
  const fetchCategories = async () => {
    try {
      const response = await apiClient.getCorpusCategories(selectedDocType);
      // Map backend categories to UI format
      const mappedCategories = response.categories.map((cat, idx) => ({
        name: cat.name,
        count: cat.count,
        id: cat.name.toLowerCase().replace(/\s+&\s+/g, '-').replace(/\s+/g, '-')
      }));
      
      setScopeCategories([
        {name: 'All', count: response.categories.reduce((sum, c) => sum + c.count, 0), id: 'all'},
        ...mappedCategories
      ]);
    } catch (err) {
      console.error('Failed to fetch categories:', err);
    }
  };
  
  fetchCategories();
}, [selectedDocType]);
```

### 3. Fix Category Filter Mapping

**Problem**: Currently mapping 'tech' → 'Technology', but backend uses full names

**Solution**: Use actual category names from backend, not hardcoded mappings

```typescript
// REMOVE this fake mapping:
const categoryMap: Record<string, string> = {
  'tech': 'Technology',
  'hr': 'Employment',
  // ...
};

// INSTEAD: Use actual category names directly
const categoryFilter = selectedCategory === 'all' ? null : selectedCategory;
```

### 4. Fix Stats Display Logic

**Current (WRONG)**:
```typescript
{ name: 'All Templates', count: stats.templates_count, id: 'all' },
```

**Fixed**:
```typescript
const scopeLabel = selectedDocType === 'template' ? 'Templates' : 
                   selectedDocType === 'public_law' ? 'Public Laws' : 'Demo Docs';
const scopeCount = selectedDocType === 'template' ? stats.templates_count :
                   selectedDocType === 'public_law' ? stats.public_laws_count :
                   stats.demo_documents_count;

{ name: `All ${scopeLabel}`, count: scopeCount, id: 'all' }
```

### 5. Fix Pagination Display Text

**Current**:
```typescript
Showing {startIndex + 1}-{endIndex} of {totalDocs} verified templates
```

**Fixed**:
```typescript
const docTypeLabel = selectedDocType === 'template' ? 'templates' :
                     selectedDocType === 'public_law' ? 'public laws' : 'demo documents';

Showing {startIndex + 1}-{endIndex} of {totalDocs} verified {docTypeLabel}
```

### 6. Verify Deployment

**Critical**: Ensure Phase 7H changes are actually deployed to production

**Check**:
1. Vercel deployment logs
2. Test live frontend: `https://lex-guard-bay.vercel.app/library`
3. Open browser console, check API calls
4. Verify it's calling `/api/v1/corpus/documents` not mock data

---

## IMPLEMENTATION STEPS

### Step 1: Backend Enhancement
- [ ] Add `/api/v1/corpus/categories` endpoint
- [ ] Add `getCorpusCategories` method to corpus routes
- [ ] Test endpoint returns correct counts per scope
- [ ] Run backend tests

### Step 2: Frontend API Client
- [ ] Add `getCorpusCategories(doc_type)` to `src/lib/api/client.ts`
- [ ] Add TypeScript types for category response

### Step 3: Frontend Library Page Rewrite
- [ ] Remove fake `Math.floor(stats.total_count / 8)` calculation
- [ ] Add `scopeCategories` state
- [ ] Fetch categories dynamically when scope changes
- [ ] Remove hardcoded category mappings
- [ ] Use actual category names in filters
- [ ] Fix pagination display text to use scope labels
- [ ] Fix "All Templates/Laws/Docs" label to match scope

### Step 4: Testing
- [ ] Test Templates scope:
  - Shows 8 categories (Tech 34, Employment 28, NDA 22, Corp 31, IP 19, Property 26, Finance 24, Privacy 16)
  - Category pills match template structure
  - Pagination shows "1-12 of 200 verified templates"
  - Page 17 shows final 8 documents
  
- [ ] Test Public Laws scope:
  - Shows 6 statutory categories
  - Category pills change to legal categories
  - Pagination shows "1-12 of 285 verified public laws"
  - Page 24 shows final 9 documents
  
- [ ] Test Demo Docs scope:
  - Shows appropriate demo categories
  - Category pills change to demo structure
  - Pagination shows "1-12 of 15 verified demo documents"
  - Page 2 shows final 3 documents

- [ ] Test scope switching:
  - Templates → Public Laws: categories change, data changes, pagination resets
  - Public Laws → Demo Docs: categories change, data changes, pagination resets
  - Demo Docs → Templates: categories change, data changes, pagination resets

- [ ] Test filters per scope:
  - Select "Technology & SaaS" in Templates → filters to 34 docs
  - Switch to Public Laws → "Technology & SaaS" category disappears
  - Select legal category → filters correctly

### Step 5: Verification
- [ ] All 129 backend tests pass
- [ ] Pyright clean
- [ ] Next.js build succeeds
- [ ] Manual testing checklist complete
- [ ] Screenshots show correct data
- [ ] No more "62" fake counts
- [ ] No more "1-6 of 6" mismatch

---

## EXPECTED BEHAVIOR AFTER FIX

### Templates Scope:
```
Stats: 200 Templates
Categories: 
  - All Templates (200)
  - Technology & SaaS (34)
  - Employment & HR (28)
  - NDA & Confidentiality (22)
  - Business & Corporate (31)
  - Intellectual Property (19)
  - Property & Real Estate (26)
  - Finance & Lending (24)
  - Privacy & Data (16)
Pagination: "Showing 1-12 of 200 verified templates" → 17 pages
```

### Public Laws Scope:
```
Stats: 285 Public Laws
Categories:
  - All Public Laws (285)
  - Corporate Governance & Formation (~48)
  - Commercial Code & Contracts (UCC) (~48)
  - Intellectual Property & Trade Secrets (~48)
  - Labor & Employment Standards (~47)
  - Privacy & Data Protection (~47)
  - Dispute Resolution & Arbitration (~47)
Pagination: "Showing 1-12 of 285 verified public laws" → 24 pages
```

### Demo Docs Scope:
```
Stats: 15 Demo Docs
Categories:
  - All Demo Docs (15)
  - Business & Corporate (4)
  - Technology & SaaS (3)
  - Property & Real Estate (2)
  - Finance & Lending (2)
  - Employment & HR (1)
  - NDA & Confidentiality (1)
  - Privacy & Data (1)
  - Intellectual Property (1)
Pagination: "Showing 1-12 of 15 verified demo documents" → 2 pages
```

---

## COMMIT MESSAGE

```
fix(phase7i): Comprehensive corpus integrity fix - eliminate fake data

CRITICAL FIXES:
1. Remove fake category count calculation (was showing 62 for everything)
2. Add dynamic category fetching per scope
3. Separate template/public-law/demo categories
4. Fix pagination labels per scope
5. Remove hardcoded category mappings
6. Ensure actual data flows from backend

Backend:
- Added /api/v1/corpus/categories endpoint
- Returns real category counts per doc_type

Frontend:
- Dynamic scopeCategories state
- Fetches categories when scope changes
- Uses actual category names in filters
- Proper pagination labels (templates/laws/docs)
- Removed all fake calculations

Verification:
- Templates: 8 categories with correct counts (34/28/22/31/19/26/24/16)
- Public Laws: 6 statutory categories with correct counts
- Demo Docs: 8 categories with small counts (4/3/2/2/1/1/1/1)
- Pagination: Correct page counts (17/24/2)
- No more "62" everywhere
- No more "1-6 of 6" mismatch

Closes: Phase 7I comprehensive corpus data integrity fix
```

---

## NEXT STEPS

1. Implement backend `/api/v1/corpus/categories` endpoint
2. Update frontend to fetch and use dynamic categories
3. Test all three scopes thoroughly
4. Verify production deployment
5. Take new screenshots showing correct data
6. Submit to Hack2Skill attempt #2

**DO NOT SUBMIT until all issues are verified fixed in production.**
