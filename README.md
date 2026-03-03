# Intent Compression Architecture (ICA)

Engineering design proposal for a clarification-first layer that reduces ambiguity-induced entropy in large-scale language models.

---

## The Core Problem

LLMs often answer the literal wording of a question, even when the intended meaning depends on unstated definitions or constraints.
When ambiguity exists, models may hedge across interpretations, increasing token usage and reducing specificity.

---

## The Proposal

ICA introduces:

1. Ambiguity Detection  
2. Minimal Clarification Question  
3. Intent Tag Construction  
4. Conditioned Answer Generation  

If ambiguity is low, the system answers immediately.

---

## Practical Benefits

- Higher precision responses  
- Lower token usage  
- Fewer coding/research agent loops  
- Improved reasoning transparency  

---

## Evaluation Metrics

- Total Tokens per Resolved Task (TTRT)  
- Agent Loop Depth Reduction (ALDR)  
- Response Specificity Index (RSI)  
- Success Rate @ Budget  

---

## Repository Contents

- ICA_Engineering_Design_Proposal.pdf  
- diagrams/architecture.png  
- LICENSE  

---

## Author

Paul Maddison  
Email: paul.maddison.delimeg@gmail.com  
LinkedIn: https://www.linkedin.com/in/paul-maddison-b83395175/
