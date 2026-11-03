Title: Can a frozen language model learn through a plasticity unit?
Date: 2026-11-03
Category: ai, engineering
Tags: ai, language-models, continual-learning, experiments
Slug: plasticity-unit-experiment
Authors: François Leblanc
Status: draft
Summary: A falsifiable test of persistent fast weights wired into a frozen model's predictions, including an initial negative result.

[Qwenputer](https://github.com/divagr18/qwenputer) put an exact computer and writable memory inside a language model. [QwenPU](https://github.com/divagr18/QwenPU) went a step further and ran a small guest model from weights stored in that memory. I kept coming back to one question: what would have to change for the *host* model to learn from an experience?

A computer that writes notes can give a model better context. It does not necessarily change the model's own prediction rule. For that, some mutable state has to be read on the path to the next token. I've started calling that small piece of machinery a **plasticity unit**.

## The hypothesis

Give a frozen model a persistent bank of fast weights. Read the bank using one of the model's hidden activations, add its output to the next-token scores, and update it after a supervised correction. The update rule is fixed; only the bank changes. Save that bank separately from the frozen checkpoint.

The first test has a deliberately narrow yes/no rule. After eight examples assigning four ball colors to either Lily or Timmy, can the model answer the same question in three *new* phrasings? The bank must reach at least 75% accuracy, beat the untouched model by at least 20 percentage points, and avoid degrading unrelated name completions by more than five points. I wrote down the prompts, thresholds, six balanced assignments, and ten presentation orders before running it.

That would show useful supervised adaptation at an output junction. It would not show autonomous learning, general reasoning improvement, or an actual circuit compiled into Qwenputer. Those are later questions.

## The first result was no

I used Karpathy's [Stories260K model](https://huggingface.co/karpathy/tinyllamas) as a cheap frozen host. A 64-element vector supplied the mutable logit adjustment. Each correction wrote the error for that example into the vector; subsequent prompts read it back. The checkpoint stayed byte-identical, and the bank survived serialization and rollback.

Held-out accuracy was **50% with the bank and 50% without it**. It barely learned the support examples either: 50.63%. A learned scalar bias scored 49.86%; nearest-neighbour lookup over the same eight examples scored 47.22%. The pre-registered hypothesis failed on this host and task.

I then tried an exploratory version with a larger 15M-parameter TinyStories model and happy/sad completions. It reached 51.25% with the bank versus 50% frozen. Nearest-neighbour lookup got 61.11%. The larger model did not rescue this simple local rule, and retrieval remained a serious comparison rather than a formality.

The final hidden state is a compact summary for the model's own next-token prediction; it may not keep the ball color distinct enough for an error-correcting write to address the right association. In the 260K model, support and test features averaged 0.700 cosine similarity for the *same* color and 0.699 for different colors. In the 15M model, the figures were 0.856 and 0.853.

I then inspected earlier layers. At intermediate layers of the 15M model, nearest-neighbour lookup reached 77.8%, while the original local update still hovered around 51%. A ridge-style fit reached 65.3% and learned most of its support examples. This was exploratory work on the already-seen prompts, so it cannot turn the failed test into a success. It does show that representation is not the whole story. The update rule and the readout matter too.

## What comes next

I'm testing a stronger frozen host next. I'll select a junction and update rule on development data, then lock a fresh test split. If that works, the next build is a deterministic stateful circuit implementing the same read and write rule. Its outputs and update traces must match the numerical reference before I can call it a compiled plasticity unit. Integrating it with Qwenputer would still need an activation or logit bridge into the host; its published token bridge does not provide one.

I'll link the preprint and code here when the circuit and locked evaluation are complete. For now, the useful result is the boundary: writable state can be connected to predictions, but the first connection did not learn the mapping I asked it to learn.
