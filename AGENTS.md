## UI/UX & Figma Design Deliverable Standard (Mandatory)
Whenever the user requests UI/UX designs, Figma mockups, layout concepts, or visual page previews:
1. **Always Use Interactive Vector HTML Prototypes (`generative_ui` + `frontend-design`)**: Never rely on blurry text-to-image raster diffusion prompts for UI mockups. Always build a self-contained, crisp HTML/Tailwind/CSS design artifact with real vector typography, clean borders, and interactive controls.
2. **Mandatory Header Architecture (Concept Switcher + Viewport Switcher)**:
   - **All Asked Number of Designs in Header**: Whenever the user asks for a specific number of designs or variations (e.g., 3, 4, 5 concepts, or "designs for X"), **all requested designs must be switchable directly in the top header navigation** as interactive tabs (e.g., `[ 1. Capsule Pills ]`, `[ 2. Story Medallions ]`, `[ 3. Mosaic Tiles ]`, `[ 4. Couture Tabs ]`, plus an optional `[ Side-by-Side ]` comparison tab). Clicking any tab instantly switches the active design displayed in the workspace.
   - **Desktop, Tablet & Mobile Viewport Buttons Next to Them**: Directly adjacent to the design concept tabs in the header, **always include responsive viewport buttons**:
     - `[ 💻 Desktop ]` (e.g. 1440px / 1280px)
     - `[ 📱 Tablet ]` (e.g. 768px / 820px)
     - `[ 📱 Mobile ]` (e.g. 375px / 390px)
     Clicking any device button dynamically resizes the preview container with smooth width transitions (`transition: width 0.4s cubic-bezier(0.16, 1, 0.3, 1)`), allowing instant responsiveness checks on any active concept.
3. **Simulated Browser & Device Frame**:
   - Embed the prototype directly inside a simulated browser/device frame (with macOS window controls, URL bar, and active resolution label) that smoothly resizes according to the active viewport.
4. **Always Export to Downloads Folder**: Whenever you generate HTML UI designs, artifacts, or prototypes for the user, you must automatically move or copy the resulting `.html` files to the user's local Downloads folder (`C:\Users\Zaid alam\Downloads`). Do this seamlessly using a shell command.

---

---

## Git & Deployment Policy (Mandatory Always)
- **Keep Changes Local**: Do **not** commit or push changes on every update. Keep all code edits local until the user explicitly asks you to commit or push.
- **Always Use PR for Main**: Whenever user asks to push to main, first push to dev branch, commit and make a PR and then merge it. Always make PR for pushing to main.