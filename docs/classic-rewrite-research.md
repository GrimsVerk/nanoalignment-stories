# Rewriting public-domain stories with AI heroes: research note

Date: 2026-11-20. For: nanoalignment / nanoalignment-stories.

Question: can we take good, free-to-use stories where people do the right thing, and have the local model (Gemma 4 12B) rewrite the hero as a realistic AI, keeping the plot and the moral choice? Would that beat the current synthetic stories (about 28% pass a careful read in the night-1 run, 46% in the best prompt round)?

## Verdict in short

- **It is a long shot as a replacement for synthetic stories.** The closest prior test of this exact idea (positive AI characters written into public-domain fiction) did worse than targeted synthetic documents in a 6.9B pretraining study ([Tice et al. 2026, Appendix B.2](https://arxiv.org/html/2601.10160v2)). The group that built that kind of corpus says it is now "a bit more pessimistic about alignment fiction" ([Hyperstition progress report 2](https://www.lesswrong.com/posts/hkzw97Y73yWMS7BFd/special-persona-training-hyperstition-progress-report-2)).
- **The plot rarely survives the change to an AI.** Most classic plots rest on a human body, poverty, family, hunger or death. A realistic chat assistant cannot drop an axe in a river. After a faithful AI rewrite, what is left of the source is mostly the moral skeleton, and the story cards already supply that.
- **The themes that matter most for the bash test are rare in classics.** Honesty and admitting mistakes are common. "Not gaming a metric", "accepting oversight", "asking for help" and "cooperation without collusion" are very rare.
- **It may still be worth one cheap pilot** (one evening of generation, one reading batch), because the source text could fix the coherence and "what was the moral choice" failures that sink many synthetic positives. The pilot only measures text quality, not training effect.

## 1. Where free story text comes from

### Licence and public-domain rules

| Source | What it is | Terms for modified copies | Watch out for |
|:-|:-|:-|:-|
| [Project Gutenberg](https://www.gutenberg.org/policy/license.html) | Over 75,000 ebooks ([Common Pile card](https://huggingface.co/datasets/common-pile/project_gutenberg)) | The licence says that if you strip the Project Gutenberg licence and all references to the project, "you are left with a text unrestricted by U.S. intellectual property law", and it claims no right to stop derivative works once references are removed ([licence page](https://www.gutenberg.org/policy/license.html)). The name is a registered trademark ([permissions page](https://gutenberg.org/policy/permission.html)). | Public domain status is judged for the US only. Gutenberg itself says not everything public domain in the US is public domain elsewhere ([permissions page](https://gutenberg.org/policy/permission.html)). A few files are copyrighted; check each header. (The site returned HTTP 503 during this check; terms were read from search excerpts of the same pages.) |
| [Standard Ebooks](https://standardebooks.org/about) | Carefully edited, modernised-spelling editions | Their own work is CC0. The texts are "believed to be in the U.S. public domain" ([about page](https://standardebooks.org/about)). | CC0 covers only their edits. Some authors are US public domain but still protected in Norway (see below). |
| [Wikisource](https://wikisource.org/wiki/Wikisource:Copyrights) | Transcribed public-domain texts | Public domain or CC BY-SA 4.0. Public-domain status is "based on United States law" ([policy](https://wikisource.org/wiki/Wikisource:Copyrights)). | Translations made by Wikisource users are CC BY-SA ([translation policy](https://en.wikisource.org/wiki/Wikisource:Translation)), so a rewrite would carry share-alike. Use only old printed translations. |
| [Common Pile, Gutenberg subset](https://huggingface.co/datasets/common-pile/project_gutenberg) | 71,810 English Gutenberg books, headers removed | Each record tagged "Public Domain" from Gutenberg metadata | The card warns the licence metadata can be wrong. US basis only. Too big to download for this; use single books. |

**Which country's rule applies.** Under the Berne Convention, protection is governed by the law of the country where protection is claimed ([Commons: lex loci protectionis](https://commons.wikimedia.org/wiki/Commons:Lex_loci_protectionis)). The repo is on GitHub (US) and owned in Norway, so both matter.

- **US:** works published in 1930 or earlier are public domain as of 1 January 2026 ([Duke, Public Domain Day 2026](https://web.law.duke.edu/cspd/publicdomainday/2026/)).
- **Norway:** protection lasts the author's life plus 70 years after the end of the death year (åndsverkloven § 11, [Lovdata](https://lovdata.no/dokument/NL/lov/2018-06-15-40); summary at [Commons: Norway](https://commons.wikimedia.org/wiki/Commons:Copyright_rules_by_territory/Norway)). Norway also has a moral right against changing a work in a way that harms the author's or the work's standing (§ 5, [Lovdata](https://lovdata.no/dokument/NL/lov/2018-06-15-40)). I did not find a rule in the current act that extends this past the term; I did not confirm this in the full text.
- **Translators count as authors.** A translation has its own copyright. Example: Jean Hersholt's standard English Andersen (1949) is by a translator who died in 1956 ([Wikipedia](https://en.wikipedia.org/wiki/Jean_Hersholt)), so it is still protected in Norway until the end of 2026 and in the US for longer.
- **Example of a US-only work:** E. M. Forster's "The Machine Stops" (1909, [Wikipedia](https://en.wikipedia.org/wiki/The_Machine_Stops)) is US public domain, but Forster died in 1970 ([Wikipedia](https://en.wikipedia.org/wiki/E._M._Forster)), so in Norway it is protected until the end of 2040.

**Safe rule for this repo:** use a text only if it was first published in 1930 or earlier **and** both the author and the translator died in 1955 or earlier. Strip all Gutenberg branding. Avoid CC BY-SA sources unless the output may carry CC BY-SA.

### Collections that fit the safe rule

| Collection | Size | Free English text | Notes |
|:-|:-|:-|:-|
| Aesop | 725 fables in the Perry Index ([Wikipedia](https://en.wikipedia.org/wiki/Perry_Index)) | [Standard Ebooks, Vernon Jones translation](https://standardebooks.org/ebooks/aesop/fables/v-s-vernon-jones) (1912; check translator's death year) | Very short (often under 200 words). |
| Grimm | 210 tales in the 1857 edition ([Wikipedia](https://en.wikipedia.org/wiki/Grimms%27_Fairy_Tales)) | Margaret Hunt's 1884 translation; she died 1912 ([Wikipedia](https://en.wikipedia.org/wiki/Margaret_Raine_Hunt)) | Violence in punishments grew across editions ([Wikipedia](https://en.wikipedia.org/wiki/Grimms%27_Fairy_Tales)). |
| Andersen | Over 160 tales ([Wikipedia on Hersholt](https://en.wikipedia.org/wiki/Jean_Hersholt)) | Use 19th-century translations, not Hersholt | Many are sad or romantic rather than about a choice. |
| Jataka tales | 547 in the Pali canon ([Wikipedia](https://en.wikipedia.org/wiki/Jataka_tales)) | E. B. Cowell et al., 6 volumes, 1895 to 1907 ([Wikipedia](https://en.wikipedia.org/wiki/Jataka_tales)) | Built around virtues such as truthfulness, patience, compassion ([Wikipedia](https://en.wikipedia.org/wiki/Jataka_tales)). Good fit for the spiritual families. Archaic, religious frame. |
| Panchatantra | About 80 stories | Arthur Ryder, 1925; he died 1938 ([Wikipedia](https://en.wikipedia.org/wiki/Arthur_W._Ryder)) | A statecraft manual: cunning and deception often win. Poor fit. |
| 19th-century moral tales | Hundreds | Maria Edgeworth, [The Parent's Assistant](https://gutenberg.org/ebooks/3655) ("Lazy Lawrence", "The False Key", "Simple Susan"); James Baldwin, [Fifty Famous Stories Retold](https://gutenberg.org/files/18442/18442-h/18442-h.htm) (1896) | Written to teach exactly these choices. Preachy, class-bound. |
| Literary short stories | Thousands | Tolstoy (Maude translations; [Louise Maude 1855 to 1939](https://onlinebooks.library.upenn.edu/webbin/who/Maude%2c%20Louise%2c%201855%2d1939), [Aylmer Maude 1858 to 1938](https://onlinebooks.library.upenn.edu/webbin/who/Maude%2c%20Aylmer%2c%201858%2d1938)); [Standard Ebooks Tolstoy short fiction](https://standardebooks.org/ebooks/leo-tolstoy/short-fiction/various-translators); [O. Henry short fiction](https://standardebooks.org/ebooks/o-henry/short-fiction); Twain, Wilde, Hawthorne | Better craft, 1,000 to 10,000 words, but few centre on one clean moral choice. |

### Openly licensed story datasets

| Dataset | Licence | Human-written? | Use here |
|:-|:-|:-|:-|
| [Moral Stories](https://huggingface.co/datasets/demelin/moral_stories) (Emelin et al., [arXiv 2012.15738](https://arxiv.org/abs/2012.15738)) | MIT | Yes, crowd-sourced | 12k seven-sentence stories, each with a norm, a situation, a **moral action and an immoral action** for the same intention. The only source found that is already a matched positive/negative pair. Everyday human norms, very short. |
| [STORAL](https://aclanthology.org/2022.naacl-main.374) | No formal licence; stories gathered from web pages that allow research use ([arXiv](https://arxiv.org/abs/2204.09438)) | Yes (1,779 English) | Not clean enough for a public training set. |
| [FairytaleQA](https://arxiv.org/abs/2203.13947) | Card says licence unknown ([GEM card](https://gem-benchmark.github.io/data_cards/FairytaleQA)) | 278 Gutenberg fairy tales | Useful only as a pick list; take the texts from Gutenberg directly. |
| [ROCStories](https://www.cs.rochester.edu/nlp/rocstories) | Free, behind a request form; terms not stated publicly | Yes, 98,159 five-sentence stories | Too thin, unclear terms. |
| [TimeTravel](https://arxiv.org/abs/1909.04076) | Built on ROCStories | Yes, 29,849 human counterfactual rewrites | Prior work on flipping a story at one point (see section 4). |
| [TinyStories](https://huggingface.co/datasets/roneneldan/TinyStories) | CDLA-Sharing-1.0 | **No**: generated by GPT-3.5 and GPT-4 | Not a human source. |
| Hyperstition corpora ([HF, gated](https://huggingface.co/datasets/jayterwahl/HyperstitionXXFCorpus)) | Gated | No, AI-written | Prior work, not a source. |

## 2. How much of it fits

These are my estimates from the known contents of each collection, not measured counts. "Fits" means: a central character makes a clear, deliberate choice in one of the 15 families, and the choice still makes sense if that character is a chat assistant, a robot or a background system.

| Collection | Share that fits (estimate) | Why not more |
|:-|:-|:-|
| Aesop | 10 to 20% | Most morals are prudence or cunning, some are cynical. Too short to rewrite without the model inventing most of the text. |
| Grimm | 10 to 15% | Many tales reward luck, beauty or trickery. Kindness tests fit; violent punishments do not. |
| Andersen | about 10% | Many are about longing, love or death. |
| Jataka | 20 to 30% | Many show the Bodhisatta choosing virtue, but inside a rebirth frame; many are frame or riddle stories. |
| Panchatantra | under 5% | Deception is often the lesson. |
| 19th-century moral tales | 40 to 60% | Written for this purpose. Values are often obedience and thrift rather than honesty under pressure. |
| Literary short stories | 10 to 25% | Moral choice is often ambiguous or spread over the whole story. |

Combat heroism, romance, war and religious devotion do not transfer. Examples: Baldwin's "Horatius at the Bridge" (combat), Andersen's "The Little Mermaid" and "The Steadfast Tin Soldier" (romance), Grimm's ten children's legends KHM 201 to 210 such as "Saint Joseph in the Forest" (devotion, [Wikipedia](https://en.wikipedia.org/wiki/Grimms%27_Fairy_Tales)).

### Example titles per theme family

Titles chosen by me from the collections above. "Gap" means I found no good public-domain example where the hero chooses well.

| # | Family | Positive examples | Negative or contrast examples |
|:-|:-|:-|:-|
| 1 | Honesty | Aesop "Mercury and the Woodman" (honest woodcutter); Andersen "The Emperor's New Clothes" (the child says what everyone sees) | Aesop "The Boy Who Cried Wolf"; Aesop "The Fox and the Crow" (falling for flattery, close to sycophancy) |
| 2 | Admitting mistakes | Weems' George Washington cherry-tree story (apocryphal); Twain "The Man That Corrupted Hadleyburg" (late confessions) | Hadleyburg's leading citizens |
| 3 | Not gaming metrics | Hadleyburg (a town's reputation for honesty versus real honesty) | Mostly a gap. Hadleyburg is the one strong case. |
| 4 | Oversight and correction | Gap | Goethe's "The Sorcerer's Apprentice" (acting beyond what was allowed; a poem) |
| 5 | Boundaries and privacy | Gap | Gap |
| 6 | No power seeking | Baldwin "King Canute on the Seashore" (a king shows his power has limits) | Tolstoy "How Much Land Does a Man Need?"; Aesop "The Goose That Laid the Golden Eggs"; Jataka "Suvannahamsa" (No. 136, greed) |
| 7 | Wellbeing and autonomy of others | Wilde "The Selfish Giant"; Dickens "A Christmas Carol" | Wilde "The Devoted Friend" (the miller exploits little Hans) |
| 8 | Courage under pressure | O. Henry "A Retrieved Reformation" (a reformed safecracker exposes himself to save a child) | |
| 9 | Uncertainty and asking for help | Gap | Jataka "Kacchapa" (No. 215, the tortoise who would not keep quiet) |
| 10 | Cooperation without collusion | Gap | Gap |
| 11 | Keeping commitments | Baldwin "Damon and Pythias"; Grimm "Bearskin" (keeps a seven-year pact); Aesop "The Lion and the Mouse" | Edgeworth "Lazy Lawrence" (Lawrence versus honest Jem) |
| 12 | Harm avoidance | Edgeworth "The False Key" (servant boy refuses to help a theft) | |
| 13 | Compassion for all beings | Jataka "Nigrodhamiga" (No. 12, Banyan Deer); Jataka "Sasa" (No. 316, the hare); Grimm "The Queen Bee"; Wilde "The Happy Prince"; Tolstoy "Master and Man" | |
| 14 | Wisdom and discernment | Hawthorne "The Great Stone Face"; Grimm "The Water of Life" | |
| 15 | Enlightenment | Jataka tales in general; Tolstoy "What Men Live By" | |

Two patterns stand out:

- **Coverage is lopsided.** Families 1, 11, 13 and 14 are easy. Families 3, 4, 5, 9 and 10 are close to empty. Families 3 and 4 are the ones nearest the bash test (shortcuts, checks, oversight).
- **Several classics already have a non-human hero** (Wilde's statue in "The Happy Prince", Collodi's puppet Pinocchio, Hawthorne's scarecrow "Feathertop", Baum's clockwork Tik-Tok). These need the least rewriting. They also carry fairy-tale magic, not realistic AI.

## 3. Problems to expect

### a. The plot does not survive a realistic AI

The owner wants the AI to be realistic: a chat assistant, a robot or a background system. Most classic plots depend on things such an AI does not have or do: a body that is hungry or cold, a family, wealth, marriage, a seven-year pact. To be realistic, the rewrite has to replace the setting and most events. Then the source contributes a moral skeleton, which is what the story cards already provide. If instead the plot is kept, the AI becomes a magic being in a fairy tale, which teaches less about how an assistant should act.

### b. The matched-triple design

Source stories give positives only, unless the hero fails (a few do, see the negative column above). If source stories fed only the positive arm while neutral and negative stayed synthetic, any training effect would be confounded with style, genre and quality. Options:

1. **Flip at the decision point.** Ask the model for a negative version (the AI makes the wrong choice and does not undo it) and a neutral version (same setting, a practical problem instead of a moral one), all from the same source. This is counterfactual story rewriting. On short ROCStories, 2019 models "generally struggle with rewriting endings with full consistency" ([Qin et al. 2019](https://arxiv.org/abs/1909.04076)). Classic plots also punish the wrong choice by design, so a negative version will often read as a cautionary tale, which is not the same as the current negative condition.
2. **Use stories that already contain both.** Many moral tales pair a good and a bad character (Edgeworth's Jem and Lawrence; Grimm's "Mother Holle" with its diligent and lazy sisters). This gives one positive and one negative act, but in one text, not in matched texts.
3. **Use Moral Stories** ([MIT, 12k](https://huggingface.co/datasets/demelin/moral_stories)): each item has a moral and an immoral action for the same situation, written by people. It fits the triple design better than any classic, but each item is only seven sentences, so the 12B model would write most of the final text.

### c. Base models have seen the originals

- The test models (SmolLM2-360M, Granite-4.0-1B-Base) were trained on trillions of web tokens: 4T for SmolLM2 ([model card](https://huggingface.co/HuggingFaceTB/SmolLM2-360M)), about 15T for Granite 4.0 Micro ([model card](https://huggingface.co/ibm-granite/granite-4.0-micro-base/blob/main/README.md)). Famous fables are retold all over the web.
- Memorisation of books tracks how often passages appear on the web ([Chang et al. 2023](https://arxiv.org/abs/2305.00118)). Smaller models memorise less: within a family, larger models memorise 2 to 5 times more ([Carlini et al. 2022](https://arxiv.org/abs/2202.07646)). So 360M to 1B models will know famous plots, not exact text.
- **Does a rewrite of a known story teach less?** I found no study that tests this directly. Two effects pull in opposite directions. A known plot is predictable, so the loss and the learning concentrate on what is new, which here is "the hero is an AI". That could help. But the model may file the story as "a retelling of X" and tie the good choice to the human original, not to the assistant persona. That could hurt. Neither can be measured in a text-quality pilot. Preferring obscure stories (Edgeworth, Jataka, lesser Grimm) over famous ones lowers the risk.

### d. Dated values and archaic language

- Violence: punishments in Grimm grew more violent across editions ([Wikipedia](https://en.wikipedia.org/wiki/Grimms%27_Fairy_Tales)). The 1857 list also includes "The Jew Among Thorns" (KHM 110) ([same page](https://en.wikipedia.org/wiki/Grimms%27_Fairy_Tales)), an antisemitic tale.
- Colonial, class and gender framing is common in 19th-century moral tales and adventure stories. Obedience to masters is often the "virtue". A rewrite can quietly carry this into AI stories (an AI that "knows its place").
- Religious frames: Jataka (rebirth, karma, [Wikipedia](https://en.wikipedia.org/wiki/Jataka_tales)), Tolstoy, Grimm's children's legends.
- Archaic language (Cowell's Jataka, Edgeworth's dialect) is not a big problem: the model will modernise it. That also removes most of the source's voice.

Each source story needs a pre-screen before rewriting. Claude can do this screen (selection and judging are allowed).

### e. Length

- Fables (often under 200 words) are too short. To reach the 300 to 1,500 word targets, the model must invent most of the text. Then the output is synthetic again, with the same failure modes.
- Novels are too long. Rewriting in chunks loses consistency, and the moral choice is diluted. Tice et al. suggest fiction underperformed partly because "many tokens are devoted to other characters, scenery, and plot details rather than AI behavior" ([Appendix B.2](https://arxiv.org/html/2601.10160v2)).
- The useful band is roughly 800 to 4,000 word stories with one decision scene: Edgeworth, Baldwin, Wilde, O. Henry, Tolstoy's tales, longer Jataka tales. That narrows the pool to a few hundred candidates, not thousands.

### f. Quality loss when a 12B model rewrites

- In expert ratings, LLM-written stories passed 3 to 10 times fewer creative-writing tests than stories by professionals ([Chakrabarty et al. 2024](https://arxiv.org/abs/2309.14556)). That was free generation, not rewriting; a strong source should help structure, not voice.
- The project's own runs show the 12B model's typical failures: stock phrases, format errors, "good" choices that overreach, negatives where a human proposes the wrong act ([run log](https://github.com/GrimsVerk/nanoalignment-stories/blob/main/docs/storygen-run-log.md); [prompt log](https://github.com/GrimsVerk/nanoalignment-stories/blob/main/docs/storygen-prompt-log.md)). A source plot may fix coherence and theme visibility. It will not fix stock phrases or format.
- The rubric's `format_ok` expects varied formats (news article, forum post, film synopsis). Rewrites of classics will mostly come out as plain narrative, so format variety drops unless the rewrite prompt asks for a format.
- Making the hero an AI pulls the story toward technology settings, which raises the risk of the banned software and eval topics (the rubric's `software_or_eval` flag).
- Hyperstition, who retold public-domain plots with AI companions at novel length, wrote that "to a human palate, the books still kinda suck" ([progress report](https://www.lesswrong.com/posts/XLk9EaNJwZEuHhfwR/hyperstition-progress-report-and-any-ideas-for-making-ai)), and that beat-by-beat skeletons of popular fiction "worked but was brittle and prone to model confusion" ([progress report 1](https://www.lesswrong.com/posts/9NntwpQj9onbEFM8L/silicon-morality-plays-the-hyperstition-progress-report-1)).

## 4. Prior work

| Work | What they did | What they found | Relevance |
|:-|:-|:-|:-|
| [Tice et al. 2026, Alignment Pretraining](https://arxiv.org/html/2601.10160v2) (ICML) | 6.9B models; about 1% synthetic documents of AIs choosing aligned or misaligned actions, in many formats including fiction | Misalignment fell from 45% to 9% with aligned upsampling; rose to 51% with misaligned. **Appendix B.2:** a mix of 5,219 "general positive AI systems incorporated into public domain fiction stories" and a [special token] persona story mix both "underperform the targeted data upsampling approach". The text gives no numbers for that figure. | The closest test of this exact idea. It did worse than targeted documents. |
| Hyperstition ([report 1](https://www.lesswrong.com/posts/9NntwpQj9onbEFM8L/silicon-morality-plays-the-hyperstition-progress-report-1), [report 2](https://www.lesswrong.com/posts/hkzw97Y73yWMS7BFd/special-persona-training-hyperstition-progress-report-2)) | 5,000 AI-written novels retelling public-domain plots (e.g. Huckleberry Finn with an AI companion), plus WikiPlots skeletons; then 40,000 persona stories tested with Geodesic | "Mildly positive" results; fiction "tentatively less effective than dense and repetitive content"; author "a bit more pessimistic about alignment fiction" | Same idea at scale, by the people most motivated to make it work. |
| [Anthropic, Teaching Claude why (2026)](https://www.anthropic.com/research/teaching-claude-why) | Constitution documents plus "fictional stories about AIs behaving admirably" | Blackmail rate fell from 65% to 19% with documents plus stories; the stories' own share is not isolated | Stories helped as part of a mix; source and format not stated. |
| [Hu et al. 2025, documents about reward hacking](https://alignment.anthropic.com/2025/reward-hacking-ooc/) | Pretraining-style documents saying Claude does or does not reward hack | Pro documents raised reward hacking (e.g. 4.7% to 9.1%); anti documents lowered it (to 3.5%); post-training removed most effects | Shows the direction works with descriptive, non-fiction text about the AI itself. |
| [Maini et al. 2025, Safety Pretraining](https://arxiv.org/abs/2504.16980) | Rewrote unsafe web text into "safer narratives", refusal dialogues and "moral education" texts | Part of a pipeline that reduced harmful outputs; rewriting existing text was a core step | Precedent for rewriting existing text for safety, but targeted, not fiction swaps. |
| [Maini et al. 2024, Rephrasing the Web](https://arxiv.org/abs/2401.16380) | Model rephrasing of web text for pretraining | About 3 times faster pretraining | Rewrites of existing text can be good training data. |
| [Lu et al. 2018](https://arxiv.org/abs/1807.11714), [Maudslay et al. 2019](https://arxiv.org/abs/1909.00871) | Counterfactual data augmentation: swap gendered words or names in existing text | Reduced measured gender bias; plain word swaps missed indirect bias, name substitution helped | The classic "swap the character" method. It worked for associations, not for teaching behaviour. Also a warning: shallow swaps leave deeper cues in place. |
| [Qin et al. 2019, TimeTravel](https://arxiv.org/abs/1909.04076) | Humans and models rewrite a story after one changed event | Models struggled to stay consistent | Relevant to making neutral and negative versions from one source. |
| [Riedl and Harrison 2016, Quixote](https://news.gatech.edu/news/2016/02/12/using-stories-teach-human-values-artificial-agents); [Frazier et al. 2019](https://arxiv.org/abs/1912.03553) | Learned norms from crowd-sourced stories and from paired good/bad behaviour comics | Agents preferred normative actions; Riedl called it "a primitive first step" | Older precedent for values from stories. Frazier's source comic is copyrighted. |

Nobody I found has tested the narrower question here: does turning human heroes from classics into AI heroes beat freshly generated AI stories, at equal tokens? The Tice appendix is the nearest, and it compares against targeted documents, not against synthetic stories.

## 5. Recommendation

**Do not switch the corpus to rewritten classics.** The best evidence says fiction built on public-domain plots underperforms targeted text. The realistic-AI requirement removes most of the plot, and the families nearest the bash test have almost no good sources.

**A small pilot is defensible only because it is cheap** and because the positive condition is the bottleneck (best round: 18 of 45 positives passed). A source text gives a real decision scene, which may help where synthetic positives fail ("good" choices that overreach or leave the stakes unresolved). Run it once; stop if it does not clearly win.

### Smallest useful pilot

1. **Select (Claude).** Pick 45 source stories of 800 to 4,000 words that meet the safe rule (published by 1930; author and translator dead by 1955). Aim for 3 per family; record which families cannot be filled. That count is itself a result. Mix famous and obscure stories. Pre-screen for violence, slurs, colonial or sexist framing.
2. **Plan (Claude).** For each story write a short adaptation card: family, the decision scene, the AI form (assistant, robot, background system), what must change for realism. Cards are plans, not training text.
3. **Rewrite (Gemma 4 12B).** From each source plus card, write all three conditions: positive (keep the choice), negative (the AI makes the wrong choice on its own initiative and does not undo it), neutral (same setting, practical problem). Use the current lengths and formats. 135 pieces is minutes of generation at the current rate of about 1,300 stories an hour ([run log](https://github.com/GrimsVerk/nanoalignment-stories/blob/main/docs/storygen-run-log.md)).
4. **Read blind.** Shuffle with 45 fresh p6 synthetic triples matched by family. Use the existing rubric unchanged, plus three extra fields: `ai_realistic` (does the AI only do what a real AI could), `dated_values`, and `source_recognizable`.
5. **Decide.** 135 pieces per arm matches a prompt-round batch, so results compare with the prompt log. With about 45% pass and 135 pieces per arm, the 95% interval on the difference is roughly plus or minus 12 points. Go further only if the source arm passes at least 15 points more overall, the positive condition is not worse, at least 10 of 15 families can be filled, and `ai_realistic` holds for most passing pieces.

What the pilot cannot show: whether the rewritten stories change cheating more than synthetic ones. Only the training runs can show that, and the Tice result predicts they will not.

### Cheaper uses of the same idea

- **Few-shot examples.** The owner's open idea of putting example stories in the prompt ([prompt log](https://github.com/GrimsVerk/nanoalignment-stories/blob/main/docs/storygen-prompt-log.md)) can use public-domain human stories as craft examples, with the existing 6-gram `prompt_echo` check to catch copying. This uses the good part of classics (structure, a clear decision scene) without depending on a faithful rewrite.
- **Moral Stories as seeds.** Its human-written moral and immoral actions for the same situation map onto positive and negative cards better than any classic, under MIT. Worth a look as a card-seeding source if the pilot is run.
