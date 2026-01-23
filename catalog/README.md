# Product & MNE Catalog Project

## Objective
Catalog all products and MNEs to understand scope and prioritize measurement efforts.

---

## Hierarchy Structure

```
Line of Business (LOB)
└── Product
    └── Success Metrics (what can be measured)
        └── MNEs (campaigns targeting this product)
```

---

## Phase 1: LOB Inventory

| LOB | Description | Status |
|-----|-------------|--------|
| Personal Banking | | Not Started |
| Credit Cards | | Not Started |
| Lending | | Not Started |
| Investments | | Not Started |
| Insurance | | Not Started |
| Wealth Management | | Not Started |
| Small Business | | Not Started |

---

## Phase 2: Product Inventory (by LOB)

### Credit Cards
| Product | Success Metrics | Status |
|---------|-----------------|--------|
| Visa Debit (VVD) | Acquisition, Activation, Usage, Tokenization | In Progress |
| Credit Card | Acquisition, Activation, Usage | Not Started |

### Personal Banking
| Product | Success Metrics | Status |
|---------|-----------------|--------|
| Chequing Account | Opening, Activation, PAC Setup | Not Started |
| Savings Account | Opening, Balance Growth | Not Started |

### Lending
| Product | Success Metrics | Status |
|---------|-----------------|--------|
| Mortgage | Application, Approval, Funding | Not Started |
| Personal Loan | Application, Approval | Not Started |
| HELOC | Application, Approval | Not Started |

---

## Phase 3: Success Metric Library (per product)

| Product | Metric | Definition | Source Table | Status |
|---------|--------|------------|--------------|--------|
| VVD | card_acquisition | Client acquired new VVD card | VISA_DR_CRD | Defined |
| VVD | card_activation | Client activated VVD card | VISA_DR_CRD | Defined |
| VVD | card_usage | Client used VVD for transaction | POS_TXN | Defined |
| VVD | wallet_provisioning | Client added to digital wallet | TOKEN_LIST | Defined |

---

## Phase 4: Layer 1 & 2 Data Assessment

### Layer 1: Experiment Metadata (tactic_evnt_hist)
- What fields exist?
- What can we leverage?
- What's missing?

### Layer 2: Campaign Metadata (Mnemonic Mapping)
- What's in CIDM_MNEMONIC_ATTRS?
- What fields need to be added?
- Primary/Secondary metric mapping status?

---

## Research Tasks

- [ ] Get list of all LOBs from mnemonic mapping
- [ ] Get list of all products per LOB
- [ ] Identify success metrics per product
- [ ] Map existing MNEs to products
- [ ] Assess Layer 1 data availability
- [ ] Assess Layer 2 data availability

---

## Notes

*Add research findings here*

