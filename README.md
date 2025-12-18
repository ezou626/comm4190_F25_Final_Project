# Chefing: Your Own Little Sous Chef
Final Project for COMM 4190 at UPenn: Chefing

![Simply delicious, intelligently done](logo1.png)



## Creators
Parsa Idehpour, Joy Wang, Eric Zou

Chefing is your AI-powered kitchen companion that create recipes designed just for you. Chefing uses advanced AI to understand your taste preferences, dietary needs, time limits, and even your mood to suggest meals that adapt as quickly as your wants can change. It learns whether you’re into quick snacks or gourmet experiments, whether you’re cutting sugar or incorporating more fiber into your diet.

Through its voice-assisted interface and smart integrations, Chefing walks you through recipes step by step, sets automatic timers, and offers ingredient substitutions when you’re missing something — or allergic to it. Beyond convenience, Chefing focuses on sustainability: minimizing food waste by creatively using leftovers and helping you shop intentionally with dynamic grocery lists.

The result? Cooking becomes less of a chore and more of a creative partnership between you and your AI sous-chef — helping you cook smarter, eat better, and live more sustainably. Chefing is the future of home cooking, designed for your life, your fridge, and your taste.

## Video Demo
https://github.com/user-attachments/assets/eb248715-a37b-4a45-93f9-f41e842b1ff3

## Journey

[Our Initial Ideas](ideas)<br>
[Selecting Chefing](introduction.md)<br>
[Prompt Development](PromptDevelopment.ipynb)

## Code Organization
The frontend is managed by npm and the backend is managed by uv.

### Backend (Root Directory)
This is a FastAPI demonstrator with a single, local user supporting a chat interface with uploads stored on machine and an sqlite database. This app also serves static files.
- Boilerplate: [.python-version](.python-version), [pyproject.toml](pyproject.toml), [uv.lock](uv.lock)
- Main Webserver Logic: [main.py](main.py)
- Prompts (Transformed Notebook): [lib.py][lib.py]

### Frontend
This is a Vite-managed frontend with TypeScript, Tailwind CSS.
- Uploads (Fridge Picture in Demo): [uploads](uploads)
- Frontend Build: [static](static)
- Frontend Source: [frontend](frontend)
