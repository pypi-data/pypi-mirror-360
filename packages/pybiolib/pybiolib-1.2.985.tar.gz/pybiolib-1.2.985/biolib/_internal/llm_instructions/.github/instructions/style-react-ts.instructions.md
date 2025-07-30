---
applyTo: "**/*.ts,**/*.tsx"
---

Apply the [general coding guidelines](./style-general.instructions.md) to all code.

# General Project Guidelines
- Use yarn instead of npm whenever relevant.
- Prefer using `export default function` over exporting at the end of the file.

# TypeScript Guidelines
- Use TypeScript for all new code
- Follow functional programming principles where possible
- Use interfaces for data structures prefixed with I like `interface IRecord`
- Prefer immutable data (const, readonly)
- Use optional chaining (?.) and nullish coalescing (??) operators

# React Guidelines
- Use functional components with hooks
- Follow the React hooks rules (no conditional hooks)
- Prefer one component per file
- Use Tailwindcss for styling
