# RentPoint Full Codebase Audit — Implementation Plan

## Bugs Found & Being Fixed

### 1. **CRITICAL: Wallet balance not debited on withdrawal approval** (admin_views.py L194)
In `admin_withdrawal_action`, when approving a withdrawal, the code does:
```python
wallet.total_withdrawn += withdrawal.amount
wallet.save()
```
It correctly increments `total_withdrawn` but **does NOT debit `wallet.balance`**. So the owner's spendable balance never decreases when a withdrawal is approved. The owner can submit unlimited withdrawals.

### 2. **CRITICAL: Pagination loses all filter params except `q`** (item_list.html)
The pagination links in `item_list.html` only preserve `q` param but not `category`, `location`, or `max_price`. If you filter by category then go to page 2, the category filter is lost.

### 3. **CRITICAL: `my_transactions` is a double-query N+1 risk** (transactions/views.py)
After fetching `transactions` queryset with `select_related` and `prefetch_related`, the view does:
```python
total_earnings = sum(t.owner_earning for t in transactions ...)
paid_count = sum(1 for t in transactions ...)
pending_count = sum(1 for t in transactions ...)
total_count = len(transactions)
```
This evaluates the queryset 4 separate times in Python. While not a DB hit per-iteration (queryset is cached), `len(transactions)` forces full evaluation. Should use `evaluate once` pattern.

### 4. **BUG: `start_rental` view computes `amount` as Decimal × int × int** (transactions/views.py L38)
`amount = item.rental_price * quantity * duration` — `rental_price` is a Decimal, but `quantity` and `duration` come from the form as Python `int`. Django's form `IntegerField` returns Python int, which works with Decimal multiplication, but no validation exists for negative durations (form has `min_value=1` so this is OK) but no `max_value` is set for `duration`. An attacker could submit `duration=999999` and create a massive amount. The form should have a sensible max.

### 5. **BUG: `_admin_nav.html` uses `pending_withdrawals_count` and `pending_verifications_count` variables that are only set in `admin_dashboard` view context**, so badge counts are missing on all other admin pages (Users, Listings, etc.).

### 6. **BUG: `item_create` view — if formset is invalid, it falls through** (listings/views.py L80-84)
If `form.is_valid()` and `formset.is_valid()` both pass, the item saves and redirects. But if formset fails (after the item was already saved), the item exists without images but the user gets an error. The item should be saved in a transaction or the formset should be validated before saving the item.

### 7. **BUG: `item_create` view — formset is instantiated without `instance` on failure** (listings/views.py L85)
On POST when form is invalid, `formset = ItemImageFormSet(request.POST, request.FILES)` — no `instance` is passed, so it won't be associated with an item. This is cosmetically wrong but not a functional bug since we haven't saved yet.

### 8. **BUG: `verifications.html` shows full NIN to admins** (site_admin/verifications.html L64)
The model docstring explicitly says NIN should only appear in the Django admin and review queue, and `masked_nin` should be used everywhere else. But the template shows `{{ submission.nin }}` (unmasked) — this is actually intentional for the review queue (staff need to verify it), but contradicts the docstring. I'll leave this since the docstring says "staff review queue" is OK for seeing the full NIN. Not a bug.

### 9. **BUG: `transaction_list.html` - customer view shows "Verified Owner" for ALL item owners unconditionally** (L239)
```html
<div class="subtle text-xs">Verified Owner</div>
```
This hardcodes "Verified Owner" for every owner, regardless of whether `transaction.owner.is_verified` is actually true.

### 10. **BUG: `start_rental.html` shows "Verified Owner" unconditionally** (L26)
```html
<div class="subtle text-xs">Listed by {{ item.owner.get_full_name|default:item.owner.username }} · Verified Owner</div>
```
Shows "Verified Owner" for ALL owners, not just verified ones.

### 11. **BUG: Mobile navbar hides Login/Signup buttons** 
At 680px breakpoint, the CSS hides `.nav-actions .btn` and `.nav-actions .user-pill` but when `nav-open` is applied, only `.nav-links` are shown (the links list). The auth buttons (Log in / Sign up) are never shown in the mobile menu — there's no rule showing them in the open state. Unauthenticated mobile users have no way to log in or sign up from the mobile menu.

### 12. **BUG: `item_update` view doesn't check the user is an item owner** (listings/views.py L94)
`item_update` uses `get_object_or_404(Item, slug=slug, owner=request.user)` which prevents cross-user access, but never checks `request.user.is_item_owner`. A customer account that somehow has items (e.g. via admin) could edit them. Minor but inconsistent.

### 13. **BUG: `item_list.html` pagination loses category, location, max_price params**
Pagination links only preserve `q`, not the other filter params.

### 14. **Duplication: `_require_item_owner` defined twice** (listings/views.py and wallet/views.py)

### 15. **Duplication: Status badge pattern repeated across 8+ templates** — the `{% if status == "paid" %}` / `{% elif %}` / `{% else %}` badge pattern is copy-pasted 8+ times.

### 16. **Responsiveness: Categories page `1fr 340px` grid not responsive**
In `categories.html`, `style="display:grid; grid-template-columns: 1fr 340px; gap: 32px;"` is an inline style with no responsive override. On mobile this will be very narrow.

### 17. **Responsiveness: `form-card` on `withdraw.html` and `checkout.html` have `max-width` in px**
These look fine since they're constrained, but the withdraw page page-header uses `max-width: 560px` inline, which is fine.

### 18. **Missing `PLATFORM_COMMISSION_PERCENT` in context processor** — the template `transaction_list.html` uses `{{ PLATFORM_COMMISSION_PERCENT }}` but this is NOT in the `site_settings` context processor. It would render as an empty string.

## Proposed Changes

### accounts models — no changes needed
### accounts views — no changes needed  
### listings views — fix item_create transaction, add is_item_owner check to item_update
### transactions views — fix my_transactions double-iteration, add max duration validation
### transactions forms — add max_value to duration field
### wallet views — N/A
### core/admin_views.py — fix admin_withdrawal_action to debit balance
### core/context_processors.py — add PLATFORM_COMMISSION_PERCENT
### templates/partials/navbar.html — fix mobile auth buttons in open menu
### transactions/templates/transaction_list.html — fix hardcoded "Verified Owner"  
### transactions/templates/start_rental.html — fix hardcoded "Verified Owner"
### listings/views.py — extract _require_item_owner to shared util, or just fix duplication
### templates/site_admin/categories.html — fix non-responsive grid
### listings/templates/listings/item_list.html — fix pagination to preserve all filter params

## Verification Plan
- Run Django check
- Manually browse key pages at 360/768/1440px
- Verify withdrawal approval correctly debits balance
- Verify pagination preserves all filters
- Verify mobile menu shows auth links
