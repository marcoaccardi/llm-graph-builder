# React + TypeScript: Coding-Time Reference

Short, pragmatic rules for day‑to‑day React work with TypeScript. Defaults align with the official React docs. Use this as a checklist and snippet library while coding.

## Contents
- Project Structure
- Components & Props
- State & Reducers
- Effects (useEffect/useLayoutEffect)
- Memoization (useMemo/useCallback/memo)
- Refs & DOM
- Lists & Keys
- Context
- Data Fetching
- Forms
- Styling
- Accessibility
- Error Handling
- Testing
- TypeScript Tips
- References
 - Stack Overrides (Vite + Tailwind + R3F)

## Project Structure
- Prefer feature‑first (domain/route) folders over type‑first. Keep related UI, hooks, and tests together.
- React doesn’t mandate structure; pick one and be consistent. Add folders only when duplication or coupling appears.
- Typical layout:
  - `src/features/<feature>/{components,hooks,api,types}`
  - `src/shared/{components,hooks,lib,ui}`
  - `src/app` (root providers, routing, layout)
- Co‑locate tests (`*.test.tsx`) and styles near components.
- Keep components focused; extract when responsibilities grow.

## Components & Props
- Prefer function components. Avoid `React.FC`; type props explicitly.
- Destructure props with sensible defaults; avoid `defaultProps` for function components.
- For primitive wrappers, expose standard HTML props via `ComponentProps<'button'>` and forward refs as needed.
- Keep renders pure: derive JSX from props/state only; no side effects in render.

Example
```tsx
import type { ComponentProps } from 'react';

type ButtonProps = {
  variant?: 'primary' | 'secondary';
} & ComponentProps<'button'>;

export function Button({ variant = 'primary', className, ...rest }: ButtonProps) {
  const cls = `${variant} ${className ?? ''}`;
  return <button className={cls} {...rest} />;
}
```

## State & Reducers
- Prefer multiple `useState` variables when values change independently; use `useReducer` for complex or coordinated updates.
- Treat state as immutable; never mutate arrays/objects in place.
- Avoid mirroring props in state. Derive during render when cheap; memoize if expensive.
- Keep derived values out of state unless needed for controlled inputs.

Reducer example
```tsx
type State = { username: string; password: string; isLoading: boolean };
type Action =
  | { type: 'username'; value: string }
  | { type: 'password'; value: string }
  | { type: 'loading'; value: boolean };

function reducer(s: State, a: Action): State {
  switch (a.type) {
    case 'username': return { ...s, username: a.value };
    case 'password': return { ...s, password: a.value };
    case 'loading':  return { ...s, isLoading: a.value };
  }
}
```

## Effects (useEffect/useLayoutEffect)
- Effects synchronize React with external systems (network, DOM APIs, subscriptions). Don’t use them to compute values you can derive during render.
- Always list all reactive dependencies. If that’s noisy, move logic into event handlers or custom hooks.
- Use `AbortController` to cancel fetches; unsubscribe/cleanup in the return function.
- Use `useLayoutEffect` only when measuring/mutating layout before paint is required.

Fetch with cleanup
```tsx
useEffect(() => {
  const ac = new AbortController();
  (async () => {
    const res = await fetch('/api/items', { signal: ac.signal });
    // setItems(await res.json());
  })().catch(() => {});
  return () => ac.abort();
}, []);
```

## Memoization (useMemo/useCallback/memo)
- Measure first; memoize to avoid expensive recalculation or to stabilize props passed to memoized children.
- `useMemo` for pure expensive values; `useCallback` for function identity; `memo` to skip child re‑renders when props are shallow‑equal.
- Avoid premature memoization; remove if it adds complexity without benefit.

## Refs & DOM
- `useRef` holds mutable, non‑reactive values or DOM nodes; updating `ref.current` doesn’t re‑render.
- Use `forwardRef` to expose inner DOM elements from components; pair with `useImperativeHandle` sparingly.

## Lists & Keys
- Provide stable, unique `key` for list items. Avoid array index as key when the list can change order, insert, or delete.

```tsx
{items.map(item => (
  <Row key={item.id} item={item} />
))}
```

## Context
- Use for values needed by many components (theme, auth, i18n). Avoid using Context as a write‑heavy global store.
- Split contexts by concern; memoize the provided `value`.

Typed context
```tsx
type Auth = { user: { id: string } | null };
const AuthContext = createContext<Auth>({ user: null });

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<Auth['user']>(null);
  const value = useMemo(() => ({ user }), [user]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
```

## Data Fetching
- Trigger fetches in handlers or Effects; prefer a data library (e.g., TanStack Query) for caching, retries, and deduping.
- Co‑locate data fetching with components; cache at boundaries to avoid waterfalls.
- Use Suspense‑based APIs if your framework/runtime supports them for loading states.

## Forms
- Prefer controlled inputs for complex validation; uncontrolled with refs is fine for simple cases.
- Keep form state localized; derive validation messages from state rather than duplicating.
- Debounce expensive validations and network checks.

## Styling
- Choose one approach and be consistent (CSS Modules, CSS‑in‑JS, Tailwind, etc.).
- Use design tokens (CSS variables or a theme object) instead of hardcoding hex colors. Keep tokens in one place.

Example tokens
```ts
// src/shared/ui/tokens.ts
export const colors = {
  bg: { base: '#fff', muted: '#f5f5f5' },
  text: { base: '#111', subtle: '#444', error: '#d00' },
} as const;
```

## Accessibility
- Prefer semantic HTML elements; add ARIA only when necessary.
- Every interactive element must be keyboard accessible and have visible focus.
- Link labels with inputs (`<label htmlFor>` + `useId`). Provide `alt` text for images.

## Error Handling
- Use Error Boundaries for rendering errors; use `try/catch` in event handlers and async flows.
- Show user‑friendly fallbacks; log errors to monitoring.

## Testing
- Use React Testing Library; test behavior, not implementation details.
- Prefer queries by role and accessible name; avoid brittle snapshots of large trees.

## TypeScript Tips
- Props: `type Props = {...}`; avoid `React.FC` and `defaultProps`.
- Events: use specific types (e.g., `ChangeEvent<HTMLInputElement>`).
- Refs: `const ref = useRef<HTMLInputElement>(null)`; with `forwardRef<HTMLInputElement, Props>(...)`.
- Utility: `ComponentProps<'button'>` for passthrough; `Omit`/`Pick` for variants; `as const` for literals; `satisfies` to verify shapes.

## Stack Overrides (Vite + Tailwind 4 + React 19 + R3F)
- Vite
  - Use `import.meta.env` for env access; prefix custom vars with `VITE_`.
  - Prefer code-splitting for heavy features (`lazy(() => import('./Big'))`).
  - Optional aliases: set `tsconfig.json: compilerOptions.paths` and mirror in `vite.config.ts: resolve.alias`.
- Tailwind 4
  - Either use the Vite plugin or PostCSS. With the Vite plugin, add `import tailwind from '@tailwindcss/vite'` and include `tailwind()` in `plugins` in `vite.config.ts`, then add `@import "tailwindcss";` at the top of your `src/index.css`.
  - Keep design tokens as CSS variables (or extend Tailwind theme) and prefer utility classes over ad-hoc inline styles.
- React Three Fiber (R3F)
  - Keep `<Canvas>` isolated; use `Suspense` around async assets (e.g., GLTF). Memoize materials/geometry and avoid allocations inside `useFrame` loops.
  - For static scenes, consider `<Canvas frameloop="demand">` and call `invalidate()` on updates.

## References
- React Docs – hooks, effects, lists/keys, context, performance, accessibility: https://react.dev/reference/react
- TypeScript‑React Cheatsheets – typing patterns: https://react-typescript-cheatsheet.netlify.app/
