# DeepGuard Solution

DeepGuard is a reinforcement-learning project that trains an automated **defender** for a simulated intrusion-prevention game. The business framing is a healthcare provider that needs its defense policy to *adapt* to attacker behavior instead of relying on static, hand-written rules — because a wrong static rule against patient data has real regulatory consequences.

## Project Goal

- Train an RL agent to defend a small network against an attacker that is trying to reach and compromise a "data" node.
- Compare two RL approaches — a tabular, on-policy method (SARSA) and a deep, off-policy method (DDQN) — against a random-defender baseline.
- Evaluate both against two attacker strategies of increasing difficulty (random attacks vs. always-strongest attacks) and understand *why* one approach wins where it does.

## Environment

Built on [gym-idsgame](https://github.com/Limmen/gym-idsgame), an abstract Markov-game model of intrusion prevention:

- The network is 4 nodes: **start → 2 servers → data**. The attacker invests in attack types; an attack on a node succeeds if its `attack_value` exceeds that node's `defense_value` for that type.
- Detection is only rolled **when an attack fails**, with probability `detection_value / 10` of the attacked node.
- Every episode ends one of two ways: the data node is **hacked** (defender reward ≈ −26), or the attacker is **detected** — in which case the defender's reward equals how much it raised the data node's minimum defense since the start (a detection with no hardening bonus pays 0). A cumulative reward of 0 is therefore not a stalemate; the notebook tracks the real outcome (`hacked` vs. `detected`) alongside the reward.
- The environment is a two-player Markov game (`step()` takes an `(attacker_action, defender_action)` pair); a `DefenderWrapper` turns it into a standard single-agent Gym interface, with the attacker move handled internally by a built-in bot.
- Two attacker scenarios: `random_attack-v21` (picks random attacks) and `maximal_attack-v21` (always uses its strongest attack).
- Evaluation protocol for every agent: 500 episodes, max 100 steps, reporting positive-reward rate, breach rate, detection rate, and average reward.

## Approach

### 0. Random-defender baseline (control group)
Establishes the reference numbers everything else is measured against.

### 1. SARSA (tabular, on-policy) — random-attack scenario
SARSA learns the value of the policy it's actually executing, exploration included — a useful bias in a security setting, since it favors conservative policies over ones that only look good under perfect greedy play (what off-policy Q-learning would estimate).

Two design problems had to be solved before the tabular agent could learn anything:
- **State compaction.** The raw 20-dim state produces ~10⁵ distinct visited states during training (most seen exactly once), so nothing generalizes. Reading the game mechanics shows the defender's score depends only on the **data node** (its 4 defense values drive the hardening bonus; its detection value drives the final detection roll). Aggregating the state to just those 5 values, capped at 3, cuts this to ~200 visited states.
- **Pessimistic initialization.** All rewards are ≤ 0 except rare hardening bonuses, so a zero-initialized Q-table is *optimistic* — every unexplored action looks better than anything already tried, wasting the training budget. Initializing Q at the baseline average return (≈ −13) removes this bias.

Hyperparameters: α = 0.05, γ = 0.99, ε decays exponentially from 1.0 to 0.02 (floor reached halfway through training), 50,000 episodes, max 100 steps per episode.

### 2. DDQN (Double Deep Q-Network) — both scenarios
Unlike the tabular agent, DDQN consumes the full 20-dim state directly — no feature engineering — and generalizes across similar defense configurations. It decouples action *selection* (online network) from action *evaluation* (target network) to counter the overestimation bias of vanilla DQN, which matters here since an overconfident defense choice can mean a breached data node:

```
y = r + γ · Q_target(s', argmax_a Q_online(s', a)) · (1 − done)
```

Stabilization choices, all motivated by the sparse, spiky reward structure:
- **Experience replay** (50k transitions) to break temporal correlation between samples.
- **Rewards scaled by 1/26** into roughly [−1, 0] so the Huber loss and learning rate behave well.
- **Huber loss + gradient clipping** against reward spikes.
- **Soft (Polyak) target updates** (τ = 0.005) instead of hard copies, for smoother bootstrap targets.
- **Best-checkpoint selection**: with ε-greedy exploration and bootstrapping, the greedy policy oscillates between evaluations; the notebook evaluates every 500 episodes over 100 episodes and keeps the best-performing weights.

Architecture: MLP 20 → 64 → 64 → 20 (ReLU), Adam (lr = 2.5·10⁻⁴), batch size 128, γ = 0.99, ε decays from 1.0 to 0.05 over the first 60% of 10,000 episodes, observations scaled by 1/9 (the max defense value). Trained separately per scenario.

### 3. Comparative analysis & conclusions
Both trained agents are compared against each other and the baseline on the same 500-episode evaluation protocol, and the results are interpreted against the game mechanics rather than taken at face value (see Results).

## Results

*(Numbers as reported in the notebook; representative of a single training run — expect run-to-run variance from RL training.)*

| Scenario | Agent | Avg. reward | Breach rate | Positive-reward episodes |
|---|---|---|---|---|
| Random attack | Baseline | −12.7 | 48.8% | ~0% |
| Random attack | SARSA | −5.1 | 20.6% | 25.2% |
| Random attack | DDQN | −4.65 | 21.4% | 52.4% |
| Maximal attack | Baseline | — | 64.6% | — |
| Maximal attack | DDQN | −4.47 | 17.2% | ~0% (82.8% detection) |

- Both trained agents dramatically beat the baseline, cutting breach rate roughly in half or better.
- **SARSA needed domain-informed state aggregation to learn at all**, but once compact it converges smoothly (~200 states) and is competitive on average reward.
- **DDQN needs no feature engineering**, extracts more of the reward structure (52% vs. 25% positive episodes on the random-attack scenario), and transfers unchanged to the harder maximal-attack scenario — at the cost of unstable training that requires checkpoint selection. This is the classic interpretability-and-stability vs. generality trade-off.
- **Why doesn't DDQN ever "win" against the maximal attacker?** It's not a training failure — it's the reward-optimal trade-off. Scoring positive requires spending the first ~4 moves hardening the data node; against an attacker that always concentrates its strongest attack, those moves are unaffordable (a scripted "harden-then-detect" policy does reach ~21% positive episodes, but gets breached ~52% of the time, avg. reward ≈ −13). The detection-focused policy DDQN converges to scores 0 on most episodes but keeps breaches at 17% — a much higher expected reward. The agent optimizes reward, not the win statistic, and with this reward design protecting the data beats accumulating points.
- **Metric design matters**: measuring "defender wins" by reward sign alone hides that every episode ends in either breach or detection; against the maximal attacker, the reward-optimal policy scores zero *on purpose*.
- **Business framing**: breach rate is what maps to regulatory exposure for patient data. The RL defender cuts simulated breaches by roughly 3–4× with no hand-written rules, and adapts its resource allocation (hardening vs. detection) to the attacker's profile.
- **Limitations**: gym-idsgame is a heavily abstracted model (small graph, integer attack/defense values, attacker bots with fixed strategies) — these results demonstrate methodology, not a deployable defense.

## Tech Stack

- **Environment**: [gym-idsgame](https://github.com/Limmen/gym-idsgame) (Markov-game IDS simulator, installed with `--no-deps` to avoid its outdated pinned dependencies)
- **Deep learning**: PyTorch (`torch`, `torch.nn`) for the DDQN network
- **Numerical / data**: NumPy, pandas
- **Visualization**: Matplotlib
- **Language / environment**: Python, Jupyter Notebook

## Run

From `Projects/DeepGuard_Solution`:

```bash
pip install torch numpy pandas matplotlib jupyter
pip install --no-deps gym-idsgame
jupyter notebook
```

Then open `DeepGuard.ipynb` and run cells top to bottom.

> `gym_idsgame` ships with a small incompatibility on recent Python/gym versions (two bot-agent modules reference `idsgame_util` without importing it) — the notebook's first code cell patches this before any environment is created, so run it first.
>
> On Google Colab: run `!pip install --no-deps gym-idsgame` and **restart the runtime** before proceeding.

## Project Structure

```text
DeepGuard_Solution/
├─ README.md
└─ DeepGuard.ipynb
```

No trained-model artifacts are persisted to disk in this project — SARSA's Q-table and DDQN's network weights live in-memory for the duration of the notebook run.
