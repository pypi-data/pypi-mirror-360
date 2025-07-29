<p align="center">
  <img src="https://github.com/gtfintechlab/ConfReady/blob/main/confready/public/confready.png?raw=true" alt="ConfReady Logo" width="300"/>
</p>

<p align="center"><strong>ConfReady</strong>: A simple tool to parse research papers and assist with conference checklists.</p>

# ConfReady

The [ARR Responsible NLP Research checklist](https://aclrollingreview.org/responsibleNLPresearch/) encourages best practices in research ethics, societal impact, and reproducibility. ConfReady helps authors reflect on their work by using **retrieval-augmented generation (RAG)** to answer checklist questions — and provides a framework to **evaluate how large language models respond to ethical prompts**.

---

## Installation

```bash
pip install confready
````
---

## Usage

To run the app:

```bash
confready run
```

Add your API keys in `confready/server/.env`:

```bash
OPENAI_API_KEY=your_key_here
TOGETHERAI_API_KEY=your_key_here
```

---

## Documentation

Visit: [https://confready-docs.vercel.app/docs/introduction](https://confready-docs.vercel.app/docs/introduction)

---

## License

Licensed under the [AGPL-3.0 License](https://www.gnu.org/licenses/agpl-3.0.html).


