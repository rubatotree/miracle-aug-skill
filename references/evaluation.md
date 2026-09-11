# Evaluate robustness without leakage

The goal is successful embodied behavior under nuisance variation. Three different
claims require different evidence: rendered scenes look plausible; generated
demonstrations are task/label valid; a trained policy generalizes better. Passing the
first two does not prove the third.

Keep all derivatives of one measured demonstration in the same source-episode split
group. Randomly splitting augmentation seeds from one trajectory into train/test leaks
motion and scene information. Hold out independent demonstrations/subjects/scenes,
as appropriate, and hold out nuisance combinations or continuous ranges beyond those
used for training. Label simulated versus real evaluation.

Plan comparisons before training: source-only baseline, source plus standard-engine
augmentation, source plus mixed-engine augmentation, and a feasible weighting ablation.
Match architecture, optimization budget, data exposure and evaluation episodes. Avoid
confounding a larger training budget with improved augmentation quality. Use the
recorded engine tiers and sample weights to test weight hypotheses, not to presume
Cycles always deserves an arbitrary multiplier.

Evaluate task success using an independent oracle, with failure categories such as
perception loss, grasp failure, collision, incorrect placement and instability.
Report trials, seeds, success rates and uncertainty intervals; stratify by nuisance
intensity/combination and real/sim domain. A single successful video is a demonstration,
not a statistically supported robustness result.

If training/evaluation is outside current authorization or compute scope, deliver
dataset coverage, validation and a concrete evaluation configuration/protocol. State
that policy generalization remains untested. Do not launch costly training merely to
complete an aspirational claim in the project description.

For photo-only synthesis, report that no measured task demonstration was used for motion
construction; separately disclose pretrained model weights, CAD, task-specific scene/
solver tuning and human corrections. Do not conflate zero recorded demonstrations with
zero prior knowledge, zero supervision, or verified zero-shot real success. The primary
video-plus-multiview workflow retains its actual measured source lineage.

Policy delivery also needs runtime correctness before task evaluation: unit/processor
identity, sequential action continuity, latency and release behavior. Read
[training-deployment.md](training-deployment.md) and
[rollout-diagnostics.md](rollout-diagnostics.md). A user-reported grasp and transfer without
release is partial progress, not a successful completed placement trial.
