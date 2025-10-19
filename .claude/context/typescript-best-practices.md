# Typescript-Best-Practices
Patterns and Best Practices for procedural Typescript/JavaScript development following the rule of 4 principle

Use the knowledge from this documentation to help you understand the codebase and implement the features.
https://www.typescriptlang.org/docs/

## Quick Reference (use while coding)

- Setup
  - Enable strong type-checking: set `"strict": true` and also turn on `"exactOptionalPropertyTypes": true` and `"noUncheckedIndexedAccess": true` in `tsconfig.json`. Prefer `"verbatimModuleSyntax": true` and `"noImplicitOverride": true` for clearer imports and class overrides. See the tsconfig baseline below.
  - Prefer `unknown` over `any` at boundaries; narrow before use.
  - Use discriminated unions and narrowing (`in`, `typeof`, `instanceof`) instead of flag booleans.
  - Prefer literal unions or `as const` objects over `enum` in most app code. Use `enum` only when you truly need it (e.g., interop with existing enums or reverse-mapping semantics).
  - Use `satisfies` to check object shapes without widening and to keep the inferred type.

- Everyday patterns
  - Add explicit return types on exported functions and public APIs; allow inference for locals.
  - Mark read-only data using `readonly` properties, `Readonly<T>`, `ReadonlyArray<T>`, and `as const`.
  - Constrain generics (`<T extends Foo>`) and provide sensible defaults (`<T = string>`). Avoid unconstrained `any`.
  - Prefer named exports; use default export only when a module has one clear primary item.
  - For errors, `catch (e: unknown) { ... }` then narrow; don’t throw strings.

- Snippets
  - Exhaustive switch with `never`:
    ```ts
    type Shape = { kind: 'circle'; r: number } | { kind: 'square'; s: number };
    function area(x: Shape) {
      switch (x.kind) {
        case 'circle': return Math.PI * x.r ** 2;
        case 'square': return x.s * x.s;
        default: const _exhaustive: never = x; return _exhaustive;
      }
    }
    ```
  - `unknown` at boundaries and narrowing:
    ```ts
    function parse(data: unknown) {
      if (typeof data === 'string') return JSON.parse(data);
      throw new Error('expected string');
    }
    ```
  - `as const` and `satisfies`:
    ```ts
    const Status = { ok: 'OK', err: 'ERR' } as const;
    type Status = typeof Status[keyof typeof Status];

    const cfg = {
      retries: 3,
      mode: 'fast',
    } satisfies { retries: number; mode: 'fast' | 'safe' };
    ```

## Recommended tsconfig baseline

Use this as a starting point for apps/libraries (adjust `lib`, `moduleResolution`, and `target` per runtime/bundler):

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "lib": ["ES2022", "DOM"],
    "strict": true,
    "exactOptionalPropertyTypes": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "useUnknownInCatchVariables": true,
    "verbatimModuleSyntax": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitReturns": true,
    "skipLibCheck": true
  }
}
```

Notes:
- For Node-only packages, consider `"moduleResolution": "nodenext"` and appropriate `"lib"` (e.g., add `"DOM"` only for browser code).
- `"exactOptionalPropertyTypes"` and `"noUncheckedIndexedAccess"` are not part of `strict`; enable them explicitly.
- `"verbatimModuleSyntax"` enforces `import type` for type-only imports and preserves import syntax.

## Working guidelines (condensed)

- Types vs interfaces
  - Use either consistently. A common approach: `interface` for object shapes/public APIs; `type` for unions, intersections, mapped/conditional types.
  - Avoid declaration merging/`namespace`; prefer modules and explicit exports.

- Narrowing and unions
  - Prefer discriminated unions with a stable `kind` field.
  - Narrow using `in`, `typeof`, `instanceof`, equality on `kind`, and user-defined type predicates.

- Functions
  - Keep parameter objects small and well-typed; avoid excessive optional fields—prefer separate call signatures (overloads) when shapes differ.
  - Use default parameters instead of `param?: T | undefined` when possible.

- Generics
  - Constrain with `extends`; provide defaults; avoid over-generic APIs—prefer specialization.
  - Use `unknown` in generic positions instead of `any` to preserve safety.

- Modules & imports
  - Prefer named exports; co-locate types with implementations; use `import type { Foo } from '...'` for type-only imports.

- Errors & async
  - Always return `Promise<T>` from async APIs; avoid mixing callbacks and promises.
  - `catch (e: unknown)`; narrow to `instanceof Error` (or shape-check) before use.

- Linting & DX
  - Use `typescript-eslint`’s `recommended` config; enable rules that ban `any` (or at least require justification) and flag unused values.

---


## Table of contents
- [4 fundamental features](#4-fundamental-features)
- [4 types of scripts](#4-types-of-scripts)
- [Script (file) Organization](#script-organization)
- [4 fundamental features in detail](#4-fundamental-features-in-detail)
  - [Primitives](#primitives)
  - [Functions](#functions)
  - [Objects](#objects)
    - [Object-literals](#object-literals)  
    - [Classes](#classes)
    - [Enums](#enums)
  - [Types](#types)
- [Naming](#naming)
  - [Files/Folders](#files-folders)
  - [General Notes](#general-naming-notes)
  - [Functions](#naming-functions)
  - [Objects](#naming-objects)
  - [Types](#naming-types)
- [Comments](#comments)
- [Imports](#imports)
- [Example Scripts](#example-scripts)
- [Misc Style](#misc-style)
- [Testing](#testing)
  - [General Notes](#testing-general-notes)
  - [Structuring BDD style tests](#testing-bdd-style)
<br/>


## 4 "Fundamental" Features <a name="4-fundamental-features"></a>
- `Primitives`, `Functions`, `Objects`, and `Types`
- <b>Primitives</b> - 5 original: `null`, `undefined`, `boolean`, `number`, `string`. Two new ones `symbol` and `bigint`. 
- <b>Functions</b> - 4 ways to create functions: function-declarations `function functionName() {}`, arrow-functions `() => {}`, placing them directly in object-literals (not counting arrows), and directly inside classes (not counting arrows).
- <b>Objects</b> - 4 ways to create objects: object-literals, enums, classes, calling functions with `new` (obsolete es5 way).
- <b>Types</b> - 2 main ways to create types: types-aliases (`type`) and interfaces (`interface`). Note: there's also function overloading for function-declarations. 
- Note: Functions are technically objects too but for all practical purposes we'll consider them separate.
<br/>


## 4 types of scripts <a name="4-types-of-scripts"></a>
- <b>Declaration</b>: exports one large declared item (i.e. a file called HttpStatusCodes.ts which exports a single enum containing all the http status codes.
- <b>Modular-Object</b>: In JavaScript, module is another term for file, so if we use a single object to represent the items available from that file, we'll call it a modular-object script. The export default is an `object-literal` containing a bunch of closely related functions/variables (i.e. a file call UserRepo.ts which has a bunch of functions for handling database queries related to user objects, we refer to it as the _UserRepo_ module).
- <b>Inventory</b>: for storing a large number of smaller declared items. (i.e. a file called types.ts which stores commonly shared types throughout your application)
- <b>Linear</b>: executes a series of commands (i.e. a file called `setup-db.ts` which does a bunch of system commands to initialize a database).
<br/>


## Script (file) Organization <a name="script-organization"></a>
- Because of how hoisting works in JavaScript, you should organize a file into these regions. Note that your file may not (and usually won't) have all of them:
  - Constants
  - Types
  - Run/Setup (Special Note: execute any logic that you need to here. Outside of linear scripts you usually shouldn't need this region, but if you do keep it short).
  - Functions
  - Export
- Some special notes about organization:
  - Only constant/readonly variables (primitive and object values) should go directly in files in the `Constants` region (except maybe in linear scripts).
  - If you are writing a linear script, it might make more sense to group your code by the task they are doing instead of by the fundamental-feature. Still, if you decide to create some function-declarations in the same script, place your function-declarations in another region at the bottom of the file below the <b>Run</b>.
  - Always put the `export default` at the very bottom of every file. This makes your default export easier to keep track of and apply any wrappers it may need.
- Organzation overview
  - Project (application or library)
  - Directory (Folder)
  - File (aka module)
  - Region
  - Section
<br/>


## 4 fundamental features in detail and when/how you should use them. <a name="4-fundamental-features-in-detail"></a>

### Primitives <a name="primitives"></a>
- To repeat: the 5 original are: `null`, `undefined`, `boolean`, `number`, `string` and the two new ones added recently are `symbol` and `bigint`.
- `symbol` is not nearly as prevalent as the others but is useful for creating unique keys on objects used in libraries. Since libraries in objects are passed around a lot, with symbols we don't have to worry about our key/value pairs getting overridden. 
- In addition to knowing what the primitives are you should know how coercion works. Coercion is when we try to call a function on a primtive and JavaScript (under the hood) wraps its object counterpart (`Boolean`, `Number`, or `String`) around it so we can make the function call, since primitives by themselves don't have functions.

### Functions <a name="functions"></a>
- As mentioned, there are function-declarations made with `function fnName() {}` and arrow-functions made with `() => {}`. Function-declarations should be used directly in files (so that we can use hoisting) and arrow functions should be used when creating functions inside of other functions (i.e. a callback passed to a JSX element). You may have to make exceptions to this when working with certain libraries cause of how `this` works in each, but generally this is how it should be done.
- When using arrow functions, only use parenthesis for the params if there are multiple params. Paranthesis are overkill if there is only one param:
```.ts
function ParentFn(param) {
   const childFn = val => ...do something with the val;
   const childFn2 = (val1, val2) => do something else;
   const badThing = (val) => ...do something else with the val;
   childFn(val);
}
```
- Functions can be be placed directly in object literals. I usually do it this way for longer multi-line functions but will use an arrow function for short functions. Note that for `direct-in-object-literal` functions The `this` keyword will refer to properties on the containing object.
```
const objLiteral = {
  helloPre: 'hello ',
  sayHello(name: string) {
    console.log(this.helloPre + name);
  },
  sayHelloAlt: (name: string) + console.log(...) // Can also use an arrow function but the `this` keyword won't refer to the parent-object literal. 
}
```

### Objects <a name="objects"></a>
- _Objects_ are lists of key/value pairs and there are 3 templates for intializing objects, <i>object-literals</i>, <i>enums</i>, and <i>classes</i>.
- Another way to initialize objects is to call a function with `new` but this is considered obsolete next to classes and leads to more complex code when doing inheritance.
- `instance-objects` are objects created from classes or calling functions with `new`. 
- All objects inherit from the parent `Object` class. We'll use the term <b>basic-object</b> to refer to objects which inherit directly from this class and no other.
- Just to point out, symbols have single key/value pair and functions also have key/values pairs and inherit from the `Function` class which in turn inherits from the `Object` class. Due to how we use these features though, we'll consider objects, functions, and symbols separate datatypes. Also note that in Javascript objects are dynamic (we can append as many properties as we want) but in Typescript the keys are static by default once the object is instantiated.

#### Object-literals <a name="object-literals"></a>
- `object-literals` are a what's created from doing key/value pairs lists with curly-braces (ie `{ name: 'john' }`) and are a convenient, shorthand way of creating basic-objects. They make it easy to both organize code and pass data around.
- When we use `export default { func1, func2, etc} as const` at the bottom of a modular-object script, we are essentially using object-literals to organize our code.
- We should generally (but not always) use object-literals over classes for organizing code for the reasons mentioned in the next section.

#### Classes <a name="classes"></a>
- Try to follow the <b>"M.I.N.T."</b> principle (<i>Multiple Instances, Not-Serialized, and Tightly-Coupled</i>) when deciding whether or not to use classes. This Medium article here explains the MINT principle in more detail:
<a target="_blank" href="https://github-readme-medium-recent-article.vercel.app/medium/@seanpmaxwell1/0">
  <img src="https://github-readme-medium-recent-article.vercel.app/medium/@seanpmaxwell1/0" alt="Recent Article 0"/>
</a>

#### Enums <a name="enums"></a>
Enums are somewhat controversial, I've heard a lot of developers say they do and don't like them. I like enums because because we can use the enum itself as a type which represents and `OR` for each of the values. We can also use an enum's value to index that enum and get the string value of the key. Here's what I recommend, don't use enums as storage for static values, use a readonly object for that with `as const`. Use enums for when the value itself doesn't matter but what matters is distinguishing that value from related values. For example, suppose there are different roles for a user for a website. The string value of each role isn't important, just that we can distinguish `Basic` from `SuperAdmin` etc. If we need to display the role in a UI somewhere, we can change the string values for each role without affecting what's saved in a database.
```typescript
// Back and front-end
enum UserRoles {
  Basic,
  Admin,
  Owner,
}

// Front-end only
const UserRolesDisplay = {
  [UserRoles.Basic]: 'Basic',
  [UserRoles.SAdmin]: 'Administrator',
  [UserRoles.Owner]: 'Owner'
} as const;

interface IUser {
  role: UserRoles; // Here we use the enum as a type
}

function printRole(role: UserRoles) {
  console.log(UserRolesDisplay[role]); // => "Basic", "Administrator", "Owner"
}
```

### Types (type-aliases and interfaces) <a name="types"></a>
- Use interfaces (`interface`) by default for describing simple structured key/value pair lists. Note that interfaces can be used to describe object-literals and classes. 
- Use type-aliases (`type`) for everything else.
<br/>


## Naming <a name="naming"></a>

### Files/Folders <a name="files-folders"></a>

#### Misc Notes
- Folders: Generally use lowercase with hyphens, but you can make exceptions for special situations (i.e. a folder in React holding Home.tsx and Home.test.tsx could be named `Home/`.
- Declaration scripts: filename should match declaration name. (i.e. if the export default is a function `useSetState()`, the filename should be `useSetState.ts`.
- Modular-object scripts: PascalCase.
- Inventory: lowercase with hyphens (shared-types.ts)
- Linear: lowercase with hyphens (setup-db.ts)
- Folders not meant to be committed as part of the final code, but may exists along other source folders, (i.e. a test folder) should start and end with a double underscore `__test-helpers__`.

#### The "common/" and "support/" subfolders
- Try to avoid naming folders `misc/` or `shared/`. These can quickly become dumping grounds for all kinds of miscellaneous content making your code disorganized. What I usually do is, if a folder has files with shared content, create a subfolder named `common/` which will only ever have these three subfolders `constants/`, `utils/` and `types/`. You can create multiple `common/` folders for different layers/sections of your application and remember to place each one's content only at the highest level that it needs to be. Here's a list of what each `common/` subfolder is for:
  - `utils/`: logic that needs to be executed (i.e. standalone functions, modular-object scripts, and classes)
  - `constants/`: static items, could be objects, arrays, or primitives
  - `types/`: for type aliases (i.e. custom utility types) and interfaces
  - <b>CHEAT</b>: If you have a very simple `common/` folder, that only has a single file that's a declaration or modular-object script, you can have just that one file in there without creating the `constants/`, `utils/` and `types/` subfolders, but remember to add these if that `common/` folder grows though. If you have an extremely small number of shared items, you can create a `common.ts/.tsx` file instead of folder.
- In short `common/` is not a grab-n-bag, `common/` is ONLY for shared types, constants, and utilities (executable logic) that are used across multiple files, nothing else.
- If you have something that isn't shared but you don't want it to go in the file that it is used in for whatever reason (i.e. a large function in an express route that generates a PDF file) create another subfolder called `support/`and place it there.

#### Example of file/folder naming using a basic express server
```
- src/
  - common/
    - constants/
      - HttpStatusCodes.ts
      - Paths.ts
      - index.ts
    - types/
      - index.ts
    - utils/
      - StringUtil.ts
      - misc.ts // A bunch of standalone functions
  - routes/
    - common/
      - Authenticator.ts // See cheat above. Authenticator.ts is a modular-object script that would never be used outside of routes/.
    - support/
      - generateUserPaymentHistoryPdf.ts // A single function used only in UserRoutes.ts but is large/complex enough to have it's own file. 
    - UserRoutes.ts
    - LoginRoutes.ts 
  - server.ts
- tests/
  - common/
    - tests/
  - user.tests.ts
  - login.tests.ts
```

### General Notes <a name="general-naming-notes"></a>
- Primitives should be declared at the top of files at the beginning of the "Constants" section and use UPPER_SNAKE_CASE (i.e. `const SALT_ROUNDS = 12`).
- Readonly arrays/objects-literals (marked with `as const`) should also be UPPER_SNAKE_CASE.
- Variables declared inside functions should be camelCase, always.
- Boolean values should generally start with an 'is' (i.e. session.isLoggedIn)
- Use `one-var-scope` declarations for a group of closely related variables. This actually leads to a slight increase in performance during minification. DON'T overuse it though. Keep only the closely related stuff together.
```typescript
// One block
const FOO_BAR = 'asdf',
 BLAH = 12,
 SOMETHING = 'asdf';

// Auth Paths
const AUTH_PATHS = [
  '/login',
  '/signup',
 ] as const;

// Errors, don't merge this with AUTH_PATHS
const ERRS = {
   Foo: 'foo',
   Bar: 'bar',
} as const;
```

### Functions <a name="naming-functions"></a>
- camelCase in most situtations but for special exceptions like jsx elements can be PascalCase.
- Generally, you should name functions in a verb format: (i.e. don't say `name()` say `getName()`).
- For functions that return data, use the `get` word for non-io data and fetch for IO data (i.e. `user.getFullName()` and `UserRepo.fetchUser()`).
- Simple functions as part of object-literals just meant to return constants don't necessarily need to be in a verb format. Example:
```typescript
const ERRORS = {
   SomeError: 'foo',
   EmailNotFound(email: string) {
      return `We're sorry, but a user with the email "${email}" was not found.`;
   },
} as const;

// Note: Errors in an immutable basic-object because we create it with an object-literal and make it immutable with 'as const'.
```
- Prepend helper functions (function declarations not meant to be used outside of their file) with an underscore (i.e. `function _helperFn() {}`).
- If you want to name a function that's already a built-in keyword, pad the name with a double underscore `__`:
```
// User.ts

function __new__(): IUser {
  return ...do stuff
}

export default { new: __new__ } as const;
```

### Objects <a name="naming-objects"></a>
- Generally, objects initialized outside of functions and directly inside of files with object-literals should be immutable (i.e. an single large `export default {...etc}` inside of a Colors.ts file) and should be appended with `as const` so that they cannot be changed. As mentioned in the <b>Variables</b> section, simple static objects/arrays can be UPPER_SNAKE_CASE. However, large objects which are the `export default` of declaration or modular-object scripts should be PascalCase.
- `instance-objects` created inside of functions or directly in the file should use camelCase.
- PascalCase for class names and any `static readonly` properties they have (i.e. Dog.Species).
- Use PascalCase for the enum name and keys. (i.e. `enum NodeEnvs { Dev = 'development'}`)
```typescript
// UserRepo.ts

// camelCase cause dynamic object
const dbCaller = initializeDatabaseLibrary();

function findById(id: number): Promise<IUser> {
  dbCaller.query()...
}

function findByName(name: string): Promise<IUser> {
  dbCaller.query()...
}

export default {
  findById,
  findByName,
} as const;


// UserService.ts

// PascalCase
import UserRepo from './UserRepo.ts'; 

// Immutable so use UPPER_SNAKE_CASE
const ERRS = {
   Foo: 'foo',
   Bar: 'bar',
} as const;

function login() {
  ...do stuff
}

...
```

### Types <a name="naming-types"></a>
- Prepend type aliases with a 'T' (i.e. `type TMouseEvent = React.MouseEvent<HtmlButtonElement>;`)
- Prepend interfaces with an 'I' (i.e. `interface IUser { name: string; email: string; }`)
<br/>


## Comments <a name="comments"></a>
- Separate files into region as follows (although this could be overkill for files with only one region, use your own discretion):
```ts
/******************************************************************************
                                RegionName (i.e. Constants)
******************************************************************************/
```
- Separate regions into sections by a `// **** "Section Name" (i.e. Shared Functions)  **** //`.
- Use `/** Comment */` above each function declaration ALWAYS. This will help the eyes when scrolling through large files. The first word in the comment should be capitalized and the sentence should end with a period.
- Use `//` for comments inside of functions. The first word in the comment should be capitalized.
- Capitalize the first letter in a comment and use a '.' at the end of complete sentences.
```typescript
/**
 * Function declaration comment.
 */
function foo() {
  // Init
  const bar = (arg: string) => arg.trim(),
    blah = 'etc';
  // Return
  return (bar(arg) + bar(arg) + bar(arg));
}
```
- If you need to put comments in an `if else` block put them above the `if` and `else` keywords:
```typescript
// blah
if (something) {
   do_something...
// foo
} else {
   do_something else...
}
```

- Don't put spaces within functions generally, but there can be exceptions like between dom elements or hooks elements in React functions. Use `//` comments to separate chunks of logic within functions. Use one space with a `/** */` comment to separate functions.
```typescript
/**
 * Some function
 */
function doThis() {
   // Some logic
   if (this) {
     console.log('dude');
   }
   // Some more logic
   ...do other stuff blah blah blah
   // Return
   return retVal;
}

/**
 * Some other function
 */
 function doThat() {
   // Some other logic
   for (const item of arr) {
      ...hello
   }
   // Last comment
   if (cool) { return 'yeah'; }
}
```

- If you have a really long function inside of another really long function (i.e. React Hook in a JSX element) you can separate them using `// ** blah ** //`.
<br/>


## Imports <a name="imports"></a>
- Try to group together similarly related imports (i.e. Service Layer and Repository Layer in an express server).
- Be generous with spacing.
- Put libraries at the top and your code below.
- Try to put code imported from the same folder towards the bottom.
- For imports that extend past the character limit (I use 80), give it a new line above and below but keep it just below the other related imports.
```
import express from 'express';
import insertUrlParams from 'inserturlparams';

import UserRepo from '@src/repos/UserRepo';
import DogRepo from '@src/repos/DogRepo';

import {
 horseDogCowPigBlah,
 horseDogCowPigBlahhhhhh,
 horseDogHelllllloooooPigBlahhhhhh,
} from '@src/repos/FarmAnimalRepo';
 

import helpers from './helpers';
```


## Example Scripts <a name="example-scripts"></a>
- Now that we've gone over the main points, let's look at some example scripts.

- A modular-object script:
```typescript
// MailUtil.ts
import logger from 'jet-logger';
import nodemailer, { SendMailOptions, Transporter } from 'nodemailer';


/******************************************************************************
                             Constants
******************************************************************************/

const SUPPORT_STAFF_EMAIL = 'do_not_reply@example.com';


/******************************************************************************
                               Types
******************************************************************************/

type TTransport = Transporter<SMTPTransport.SentMessageInfo>;


/******************************************************************************
                               Run (Setup)
******************************************************************************/

const mailer = nodemailer
 .createTransport({ ...settings })
 .verify((err, success) => {
   if (!!err) {
     logger.err(err);
   }
 });
 

/******************************************************************************
                               Functions
******************************************************************************/

/**
 * Send an email anywhere.
 */
function sendMail(to: string, from: string, subject: string, body: string): Promise<void> {
   await mailer.send({to, from, subject, body});
}

/**
 * Send an email to your application's support staff.
 */
function sendSupportStaffEmail(from, subject, body): Promise<void> {
   await mailer.send({to: SUPPORT_STAFF_EMAIL, from, subject, body});
}


/******************************************************************************
                               Export default
******************************************************************************/

export default {
   sendMail,
   sendSupportStaffEmail,
} as const;
```

- An inventory script
```.tsx
// shared-buttons.tsx

/******************************************************************************
                               Components
******************************************************************************/

/**
 * Close a html dialog box.
 */
export function CloseBtn() {
    return (
        <button css={{ color: 'grey' }}>
         Close
        </button>
    );
}

/**
 * Cancel editing a html form.
 */
export function CancelBtn() {
    return (
        <button css={{ color: 'red' }}>
         Cancel
        </button>
    );
} 
```

- A declaration script:
```typescript
// EnvVars.ts

export default {
    port: process.env.PORT,
    host: process.env.Host,
    databaseUsername: process.env.DB_USERNAME,
    ...etc,
} as const;
```

- A linear script:
```typescript
// server.ts
import express from 'express';


/******************************************************************************
                                 Run (Setup)
******************************************************************************/

const app = express(); 

app.use(middleware1);
app.use(middleware2);

doSomething();
doSomethingElse();


/******************************************************************************
                               Export default
******************************************************************************/

export default app;
```
<br/>


## Misc Style (Don't need to mention things covered by the linter) <a name="misc-style"></a> 
- Wrap boolean statements in parenthesis to make them more readable (i.e `(((isFoo && isBar) || isBar) ? retThis : retThat)`)
- Use optional chaining whenever possible. Don't do `foo && foo.bar` do `foo?.bar`.
- Use null coalescing `??` whenever possible. Don't do `(str || '') do `(str ?? '')`.
- For boolean statements, put the variable to the left of the constant, not the other way around:
```
// Don't do
if (5 === value) {

// Do do
if (value === 5) {
```
- For Typescript, specify a return type if you are using the function elsewhere in your code. However, always specifying a return type when your function is just getting passed to a library could be overkill (i.e. a router function passed to an express route). Another exception could be JSX function where it's obvious a JSX.Elements is what's getting returned.
- For if statements that are really long, put each boolean statement on it's own line, and put the boolean operator and the end of each statement. For nested boolean statements, use indentation:
```typescript
  if (
    data?.foo.trim() &&
    data?.bar && (
      role !== ADMIN || 
      data?.id !== 3 || 
      name !== ''
    )
  ) {
     ...doSomething
  }
```
- When passing object-literals as parameters to function calls, put the first curly brace on the same line as the previous parameter, as following parameters on the same line as the last curly brace:
```typescript
// Good
fooBar('hello', {
  name: 'steve',
  age: 13,
}, 'how\'s it going?');

// Bad (I see this too much)
fooBar(
  'hello',
  {
    name: 'steve',
    age: 13,
  },
  'how\'s it going?'
);

function fooBar(beforeMsg: string, person: IPerson, afterMsg: string): void {
  ..do stuff
}
```
<br/>


## Testing <a name="testing"></a>

### General Notes <a name="testing-general-notes"></a>
- Anything that changes based on user interaction should be unit-tested.
- All phases of development should include unit-tests.
- Developers should write their own unit-tests.
- Integration tests should test any user interaction that involves talking to the back-end.
- Integration tests may be overkill for startups especially in the early stages.
- Integration tests should be done by a dedicated integration tester who's fluent with the framework in a separate repository.
- Another good reasons for tests are they make code more readable.
- Errors in integration tests should be rare as unit-tests should weed out most of them.

### Structuring BDD style tests <a name="testing-bdd-style"></a>
- Declare all your variables (except constants) in the `beforeEach`/`beforeAll` callbacks, even ones that don't require asynchronous-initialization. This makes your code cleaner so that everything is declared and initialized in the same place.
- Static constants should go outside of the top level `describe` hook and should go in the `Constants` region like with other scripts. This saves the test runner from having the reinitialize them everytime.
- The tests should should go in a new region between the `Setup` and `Functions` regions.
```ts
import supertest, { TestAgent } from 'supertest';
import { IUser } from '@src/modes/User';
import UserRepo from '@src/repos/UserRepo';


/******************************************************************************
                              Constants
******************************************************************************/

const FOO_BAR = 'asdfasdf';


/******************************************************************************
                               Tests
******************************************************************************/

describe(() => {

  // Declare here
  let testUser: IUser,
    apiCaller: TestAgent;

  // Initialize here
  beforeEach(async () => {
    testUser = User.new();
    await UserRepo.save(testUser);
    apiCaller = supertest.agent();
  });

  describe('Fetch User API', () => {

    it('should return a status of 200 and a user object if the request was ' +
      'successful', async () => {
      const resp = await apiCaller.get(`api/users/fetch/${testUser.id}`);
      expect(resp.status).toBe(200);
      expect(resp.body.user).toEqual(testUser);
    });

    it('should return a status of 404 if the user was not found', async () => {
      const resp = await apiCaller.get(`api/users/fetch/${12341234}`);
      expect(resp.status).toBe(404);
    })
  });
});


/******************************************************************************
                               Functions
******************************************************************************/

/**
 * Send an email anywhere.
 */
function _someHelperFn(): void {
   ...do stuff
}
```

TypeScript Style Guide
Introduction
TypeScript Style Guide provides a concise set of conventions and best practices for creating consistent, maintainable code.

Table of Contents
Expand
Introduction
Table of Contents
About Guide
TLDR
Types
Functions
Variables
Naming
Source Organization
Appendix - React
Appendix - Tests
About Guide
What
Since "consistency is the key", TypeScript Style Guide strives to enforce the majority of rules using automated tools such as ESLint, TypeScript, Prettier, etc. However, certain design and architectural decisions must still be followed, as described in the conventions below.

Why
As project grow in size and complexity, maintaining code quality and ensuring consistent practices become increasingly challenging.
Defining and following a standard approach to writing TypeScript applications leads to a consistent codebase and faster development cycles.
No need to discuss code styles during code reviews.
Saves team time and energy.
Disclaimer
Like any code style guide, this one is opinionated, setting conventions (sometimes arbitrary) to govern our code.

You don't have to follow every convention exactly as written, decide what works best for your product and team to maintain consistency in your codebase.

Requirements
This Style Guide requires:

TypeScript v5
typescript-eslint v8 with strict-type-checked configuration enabled.
The Style Guide assumes but is not limited to using:

React for frontend conventions
Playwright and Vitest for testing conventions
TLDR
Embrace const assertions for type safety and immutability. ⭣
Strive for data immutability using types like Readonly and ReadonlyArray. ⭣
Make the majority of object properties required (use optional properties sparingly). ⭣
Embrace discriminated unions. ⭣
Avoid type assertions in favor of proper type definitions. ⭣
Strive for functions to be pure, stateless, and have single responsibility. ⭣
Maintain consistent and readable naming conventions throughout the codebase. ⭣
Use named exports. ⭣
Organize code by feature and collocate related code as close as possible. ⭣
Types
When creating types, consider how they would best describe our code.
Being expressive and keeping types as narrow as possible offers several benefits to the codebase:

Increased Type Safety - Catch errors at compile time, as narrowed types provide more specific information about the shape and behavior of your data.
Improved Code Clarity - Reduces cognitive load by providing clearer boundaries and constraints on your data, making your code easier for other developers to understand.
Easier Refactoring - With narrower types, making changes to your code becomes less risky, allowing you to refactor with confidence.
Optimized Performance - In some cases, narrow types can help the TypeScript compiler generate more optimized JavaScript code.
Type Inference
As a rule of thumb, explicitly declare types only when it helps to narrow them.


Note
Explicitly declare types when doing so helps to narrow them:

// ❌ Avoid
const employees = new Map(); // Inferred as wide type 'Map<any, any>'
employees.set('Lea', 17);
type UserRole = 'admin' | 'guest';
const [userRole, setUserRole] = useState('admin'); // Inferred as 'string', not the desired narrowed literal type

// ✅ Use explicit type declarations to narrow the types.
const employees = new Map<string, number>(); // Narrowed to 'Map<string, number>'
employees.set('Gabriel', 32);
type UserRole = 'admin' | 'guest';
const [userRole, setUserRole] = useState<UserRole>('admin'); // Explicit type 'UserRole'


Avoid explicitly declaring types when they can be inferred:

// ❌ Avoid
const userRole: string = 'admin'; // Inferred as wide type 'string'
const employees = new Map<string, number>([['Gabriel', 32]]); // Redundant type declaration
const [isActive, setIsActive] = useState<boolean>(false); // Redundant, inferred as 'boolean'

// ✅ Use type inference.
const USER_ROLE = 'admin'; // Inferred as narrowed string literal type 'admin'
const employees = new Map([['Gabriel', 32]]); // Inferred as 'Map<string, number>'
const [isActive, setIsActive] = useState(false); // Inferred as 'boolean'

Data Immutability
Immutability should be a key principle. Wherever possible, data should remain immutable by leveraging types like Readonly and ReadonlyArray.

Using readonly types prevents accidental data mutations and reduces the risk of bugs caused by unintended side effects, ensuring data integrity throughout the application lifecycle.
When performing data processing, always return new arrays, objects, or other reference-based data structures. To minimize cognitive load for future developers, strive to keep data objects flat and concise.
Use mutations sparingly, only in cases where they are truly necessary, such as when dealing with complex objects or optimizing for performance.
// ❌ Avoid data mutations
const removeFirstUser = (users: Array<User>) => {
  if (users.length === 0) {
    return users;
  }
  return users.splice(1);
};

// ✅ Use readonly type to prevent accidental mutations
const removeFirstUser = (users: ReadonlyArray<User>) => {
  if (users.length === 0) {
    return users;
  }
  return users.slice(1);
  // Using arr.splice(1) errors - Function 'splice' does not exist on 'users'
};

Required & Optional Object Properties
Strive to have the majority of object properties required and use optional properties sparingly.

This approach reflects designing type-safe and maintainable code:

Clarity and Predictability - Required properties make it explicit which data is always expected. This reduces ambiguity for developers using or consuming the object, as they know exactly what must be present.
Type Safety - When properties are required, TypeScript can enforce their presence at compile time. This prevents runtime errors caused by missing properties.
Avoids Overuse of Optional Chaining - If too many properties are optional, it often leads to extensive use of optional chaining (?.) to handle potential undefined values. This clutters the code and obscures its intent.
If introducing many optional properties truly can't be avoided, utilize discriminated union types.

// ❌ Avoid optional properties when possible, as they increase complexity and ambiguity
type User = {
  id?: number;
  email?: string;
  dashboardAccess?: boolean;
  adminPermissions?: ReadonlyArray<string>;
  subscriptionPlan?: 'free' | 'pro' | 'premium';
  rewardsPoints?: number;
  temporaryToken?: string;
};

// ✅ Prefer required properties. If optional properties are unavoidable,
// use a discriminated union to make object usage explicit and predictable.
type AdminUser = {
  role: 'admin';
  id: number;
  email: string;
  dashboardAccess: boolean;
  adminPermissions: ReadonlyArray<string>;
};

type RegularUser = {
  role: 'regular';
  id: number;
  email: string;
  subscriptionPlan: 'free' | 'pro' | 'premium';
  rewardsPoints: number;
};

type GuestUser = {
  role: 'guest';
  temporaryToken: string;
};

// Discriminated union type 'User' ensures clear intent with no optional properties
type User = AdminUser | RegularUser | GuestUser;

const regularUser: User = {
  role: 'regular',
  id: 212,
  email: 'lea@user.com',
  subscriptionPlan: 'pro',
  rewardsPoints: 1500,
  dashboardAccess: false, // Error: 'dashboardAccess' property does not exist
};

Discriminated Union
If there's only one TypeScript feature to choose from, embrace discriminated unions.

Discriminated unions are a powerful concept to model complex data structures and improve type safety, leading to clearer and less error-prone code.
You may encounter discriminated unions under different names such as tagged unions or sum types in various programming languages as C, Haskell, Rust (in conjunction with pattern-matching).

Discriminated unions advantages:

As mentioned in Required & Optional Object Properties, Args as Discriminated Type and Props as Discriminated Type, discriminated unions remove optional object properties, reducing complexity.

Exhaustiveness check - TypeScript can ensure that all possible variants of a type are implemented, eliminating the risk of undefined or unexpected behavior at runtime.


📏 Rule
type Circle = { kind: 'circle'; radius: number };
type Square = { kind: 'square'; size: number };
type Triangle = { kind: 'triangle'; base: number; height: number };

// Create discriminated union 'Shape', with 'kind' property to discriminate the type of object.
type Shape = Circle | Square | Triangle;

// TypeScript warns us with errors in calculateArea function
const calculateArea = (shape: Shape) => {
  // Error - Switch is not exhaustive. Cases not matched: "triangle"
  switch (shape.kind) {
    case 'circle':
      return Math.PI * shape.radius ** 2;
    case 'square':
      return shape.size * shape.width; // Error - Property 'width' does not exist on type 'square'
  }
};

Avoid code complexity introduced by flag variables.

Clear code intent, as it becomes easier to read and understand by explicitly indicating the possible cases for a given type.

TypeScript can narrow down union types, ensuring code correctness at compile time.

Discriminated unions make refactoring and maintenance easier by providing a centralized definition of related types. When adding or modifying types within the union, the compiler reports any inconsistencies throughout the codebase.

IDEs can leverage discriminated unions to provide better autocompletion and type inference.

Type-Safe Constants With Satisfies
The as const satisfies syntax is a powerful TypeScript feature that combines strict type-checking and immutability for constants. It is particularly useful when defining constants that need to conform to a specific type.

Key benefits:

Immutability with as const
Ensures the constant is treated as readonly.
Narrows the types of values to their literals, preventing accidental modifications.
Validation with satisfies
Ensures the object conforms to a broader type without widening its inferred type.
Helps catch type mismatches at compile time while preserving narrowed inferred types.
Array constants:

type UserRole = 'admin' | 'editor' | 'moderator' | 'viewer' | 'guest';

// ❌ Avoid constant of wide type
const DASHBOARD_ACCESS_ROLES: ReadonlyArray<UserRole> = ['admin', 'editor', 'moderator'];

// ❌ Avoid constant with incorrect values
const DASHBOARD_ACCESS_ROLES = ['admin', 'contributor', 'analyst'] as const;

// ✅ Use immutable constant of narrowed type
const DASHBOARD_ACCESS_ROLES = ['admin', 'editor', 'moderator'] as const satisfies ReadonlyArray<UserRole>;


Object constants:

type OrderStatus = {
  pending: 'pending' | 'idle';
  fulfilled: boolean;
  error: string;
};

// ❌ Avoid mutable constant of wide type
const IDLE_ORDER: OrderStatus = {
  pending: 'idle',
  fulfilled: true,
  error: 'Shipping Error',
};

// ❌ Avoid constant with incorrect values
const IDLE_ORDER = {
  pending: 'done',
  fulfilled: 'partially',
  error: 116,
} as const;

// ✅ Use immutable constant of narrowed type
const IDLE_ORDER = {
  pending: 'idle',
  fulfilled: true,
  error: 'Shipping Error',
} as const satisfies OrderStatus;

Template Literal Types
Embrace template literal types as they allow you to create precise and type-safe string constructs by interpolating values. They are a powerful alternative to using the wide string type, providing better type safety.

Adopting template literal types brings several advantages:

Prevent errors caused by typos or invalid strings.
Provide better type safety and autocompletion support.
Improve code maintainability and readability.
Template literal types are useful in various practical scenarios, such as:

String Patterns - Use template literal types to enforce valid string patterns.

// ❌ Avoid
const appVersion = '2.6';
// ✅ Use
type Version = `v${number}.${number}.${number}`;
const appVersion: Version = 'v2.6.1';

API Endpoints - Use template literal types to restrict values to valid API routes.

// ❌ Avoid
const userEndpoint = '/api/usersss'; // Type 'string' - Typo 'usersss': the route doesn't exist, leading to a runtime error.
// ✅ Use
type ApiRoute = 'users' | 'posts' | 'comments';
type ApiEndpoint = `/api/${ApiRoute}`; // Type ApiEndpoint = "/api/users" | "/api/posts" | "/api/comments"
const userEndpoint: ApiEndpoint = '/api/users';


Internationalization Keys - Avoid relying on raw strings for translation keys, which can lead to typos and missing translations. Use template literal types to define valid translation keys.

// ❌ Avoid
const homeTitle = 'translation.homesss.title'; // Type 'string' - Typo 'homesss': the translation doesn't exist, leading to a runtime error.
// ✅ Use
type LocaleKeyPages = 'home' | 'about' | 'contact';
type TranslationKey = `translation.${LocaleKeyPages}.${string}`; // Type TranslationKey = `translation.home.${string}` | `translation.about.${string}` | `translation.contact.${string}`
const homeTitle: TranslationKey = 'translation.home.title';


CSS Utilities - Avoid raw strings for color values, which can lead to invalid or non-existent colors. Use template literal types to enforce valid color names and values.

// ❌ Avoid
const color = 'blue-450'; // Type 'string' - Color 'blue-450' doesn't exist, leading to a runtime error.
// ✅ Use
type BaseColor = 'blue' | 'red' | 'yellow' | 'gray';
type Variant = 50 | 100 | 200 | 300 | 400;
type Color = `${BaseColor}-${Variant}` | `#${string}`; // Type Color = "blue-50" | "blue-100" | "blue-200" ... | "red-50" | "red-100" ... | #${string}
const iconColor: Color = 'blue-400';
const customColor: Color = '#AD3128';


Database queries - Avoid using raw strings for table or column names, which can lead to typos and invalid queries. Use template literal types to define valid tables and column combinations.

// ❌ Avoid
const query = 'SELECT name FROM usersss WHERE age > 30'; // Type 'string' - Typo 'usersss': table doesn't exist, leading to a runtime error.
// ✅ Use
type Table = 'users' | 'posts' | 'comments';
type Column<TTableName extends Table> =
  TTableName extends 'users' ? 'id' | 'name' | 'age' :
  TTableName extends 'posts' ? 'id' | 'title' | 'content' :
  TTableName extends 'comments' ? 'id' | 'postId' | 'text' :
  never;

type Query<TTableName extends Table> = `SELECT ${Column<TTableName>} FROM ${TTableName} WHERE ${string}`;
const userQuery: Query<'users'> = 'SELECT name FROM users WHERE age > 30'; // Valid query
const invalidQuery: Query<'users'> = 'SELECT title FROM users WHERE age > 30'; // Error: 'title' is not a column in 'users' table.


Type any & unknown
any data type must not be used as it represents literally “any” value that TypeScript defaults to and skips type checking since it cannot infer the type. As such, any is dangerous, it can mask severe programming errors.

When dealing with ambiguous data type use unknown, which is the type-safe counterpart of any.
unknown doesn't allow dereferencing all properties (anything can be assigned to unknown, but unknown isn’t assignable to anything).

// ❌ Avoid any
const foo: any = 'five';
const bar: number = foo; // no type error

// ✅ Use unknown
const foo: unknown = 5;
const bar: number = foo; // type error - Type 'unknown' is not assignable to type 'number'

// Narrow the type before dereferencing it using:
// Type guard
const isNumber = (num: unknown): num is number => {
  return typeof num === 'number';
};
if (!isNumber(foo)) {
  throw Error(`API provided a fault value for field 'foo':${foo}. Should be a number!`);
}
const bar: number = foo;

// Type assertion
const bar: number = foo as number;

Type & Non-nullability Assertions
Type assertions user as User and non-nullability assertions user!.name are unsafe. Both only silence TypeScript compiler and increase the risk of crashing application at runtime.
They can only be used as an exception (e.g. third party library types mismatch, dereferencing unknown etc.) with a strong rational for why it's introduced into the codebase.

type User = { id: string; username: string; avatar: string | null };
// ❌ Avoid type assertions
const user = { name: 'Nika' } as User;
// ❌ Avoid non-nullability assertions
renderUserAvatar(user!.avatar); // Runtime error

const renderUserAvatar = (avatar: string) => {...}

Type Errors
When a TypeScript error cannot be mitigated, use @ts-expect-error as a last resort to suppress it.

This directive notifies the compiler when the suppressed error no longer exists, ensuring errors are revisited once they’re obsolete, unlike @ts-ignore, which can silently linger even after the error is resolved.

Always use @ts-expect-error with a clear description explaining why it is necessary.
Avoid @ts-ignore, as it does not track suppressed errors.

📏 Rule
// ❌ Avoid @ts-ignore as it will do nothing if the following line is error-free.
// @ts-ignore
const newUser = createUser('Gabriel');

// ✅ Use @ts-expect-error with description.
// @ts-expect-error: This library function has incorrect type definitions - createUser accepts string as an argument.
const newUser = createUser('Gabriel');


Type Definition
TypeScript provides two options for defining types: type and interface. While these options have some functional differences, they are interchangeable in most cases. To maintain consistency, choose one and use it consistently.

Define all types using type alias 
📏 Rule

Note
// ❌ Avoid interface definitions
interface UserRole = 'admin' | 'guest'; // Invalid - interfaces can't define type unions

interface UserInfo {
  name: string;
  role: 'admin' | 'guest';
}

// ✅ Use type definition
type UserRole = 'admin' | 'guest';

type UserInfo = {
  name: string;
  role: UserRole;
};


When performing declaration merging (e.g. extending third-party library types), use interface and disable the lint rule where necessary.

// types.ts
declare namespace NodeJS {
  // eslint-disable-next-line @typescript-eslint/consistent-type-definitions
  export interface ProcessEnv {
    NODE_ENV: 'development' | 'production';
    PORT: string;
    CUSTOM_ENV_VAR: string;
  }
}

// server.ts
app.listen(process.env.PORT, () => {...}

Array Types
Array types should be defined using generic syntax 
📏 Rule

Note
// ❌ Avoid
const x: string[] = ['foo', 'bar'];
const y: readonly string[] = ['foo', 'bar'];

// ✅ Use
const x: Array<string> = ['foo', 'bar'];
const y: ReadonlyArray<string> = ['foo', 'bar'];

Type Imports and Exports
TypeScript allows specifying a type keyword on imports to indicate that the export exists only in the type system, not at runtime.

Type imports must always be separated:

Tree Shaking and Dead Code Elimination: If you use import for types instead of import type, the bundler might include the imported module in the bundle unnecessarily, increasing the size. Separating imports ensures that only necessary runtime code is included.
Minimizing Dependencies: Some modules may contain both runtime and type definitions. Mixing type imports with runtime imports might lead to accidental inclusion of unnecessary runtime code.
Improves code clarity by making the distinction between runtime dependencies and type-only imports explicit.

📏 Rule
// ❌ Avoid using `import` for both runtime and type
import { MyClass } from 'some-library';

// Even if MyClass is only a type, the entire module might be included in the bundle.

// ✅ Use `import type`
import type { MyClass } from 'some-library';

// This ensures only the type is imported and no runtime code from "some-library" ends up in the bundle.

Services & Types Generation
Documentation becomes outdated the moment it's written, and worse than no documentation is wrong documentation. The same applies to types when describing the modules your app interacts with, such as APIs, messaging protocols and databases.

For external services, such as REST, GraphQL, and MQ it's crucial to generate types from their contracts, whether they use Swagger, schemas, or other sources (e.g. openapi-ts, graphql-config). Avoid manually declaring and maintaining types, as they can easily fall out of sync.

As an exception, only manually declare types when no options are available, such as when there is no documentation for the service, data cannot be fetched to retrieve a contract, or the database cannot be accessed to infer types.

Functions
Function conventions should be followed as much as possible (some of the conventions derive from functional programming basic concepts):

General
Function:

should have single responsibility.
should be stateless where the same input arguments return same value every single time.
should accept at least one argument and return data.
should not have side effects, but be pure. Implementation should not modify or access variable value outside its local environment (global state, fetching etc.).
Single Object Arg
To keep function readable and easily extensible for the future (adding/removing args), strive to have single object as the function arg, instead of multiple args.
As an exception this does not apply when having only one primitive single arg (e.g. simple functions isNumber(value), implementing currying etc.).

// ❌ Avoid having multiple arguments
transformUserInput('client', false, 60, 120, null, true, 2000);

// ✅ Use options object as argument
transformUserInput({
  method: 'client',
  isValidated: false,
  minLines: 60,
  maxLines: 120,
  defaultInput: null,
  shouldLog: true,
  timeout: 2000,
});

Required & Optional Args
Strive to have majority of args required and use optional sparingly.
If the function becomes too complex, it probably should be broken into smaller pieces.
An exaggerated example where implementing 10 functions with 5 required args each, is better then implementing one "can do it all" function that accepts 50 optional args.

Args as Discriminated Type
When applicable use discriminated union type to eliminate optional properties, which will decrease complexity on function API and only required properties will be passed depending on its use case.

// ❌ Avoid optional properties as they increase complexity and ambiguity in function APIs
type StatusParams = {
  data?: Products;
  title?: string;
  time?: number;
  error?: string;
};

// ✅ Prefer required properties. If optional properties are unavoidable,
// use a discriminated union to represent distinct use cases with required properties.
type StatusSuccessParams = {
  status: 'success';
  data: Products;
  title: string;
};

type StatusLoadingParams = {
  status: 'loading';
  time: number;
};

type StatusErrorParams = {
  status: 'error';
  error: string;
};

// Discriminated union 'StatusParams' ensures predictable function arguments with no optional properties
type StatusParams = StatusSuccessParams | StatusLoadingParams | StatusErrorParams;

export const parseStatus = (params: StatusParams) => {...

Return Types
Requiring explicit return types improves safety, catches errors early, and helps with long-term maintainability. However, excessive strictness can slow development and add unnecessary redundancy.

As a rule of thumb, be explicit on the outside, implicit on the inside. For example, when building APIs or libraries, always type everything explicitly to avoid accidental breaking changes. For internal logic, let TypeScript infer its defaults, which will provide strong type safety without added verbosity.

Consider the advantages of explicitly defining the return type of a function:

Improves Readability: Clearly specifies what type of value the function returns, making the code easier to understand for those calling the function.
Avoids Misuse: Ensures that calling code does not accidentally attempt to use an undefined value when no return value is intended.
Surfaces Type Errors Early: Helps catch potential type errors during development, especially when code changes unintentionally alter the return type.
Simplifies Refactoring: Ensures that any variable assigned to the function's return value is of the correct type, making refactoring safer and more efficient.
Encourages Design Discussions: Similar to Test-Driven Development (TDD), explicitly defining function arguments and return types promotes discussions about a function's functionality and interface ahead of implementation.
Optimizes Compilation: While TypeScript's type inference is powerful, explicitly defining return types can reduce the workload on the TypeScript compiler, improving overall performance.
As context matters, use explicit return types when they add clarity and safety.

Explicitly defining the return type of a function is encouraged, although not required 
📏 Rule
Variables
Const Assertion
Strive declaring constants using const assertion as const:

Constants are used to represent values that are not meant to change, ensuring reliability and consistency in a codebase. Using const assertions further enhances type safety and immutability, making your code more robust and predictable.

Type Narrowing - Using as const ensures that literal values (e.g., numbers, strings) are treated as exact values instead of generalized types like number or string.
Immutability - Objects and arrays get readonly properties, preventing accidental mutations.
Examples:

Objects

// ❌ Avoid
const FOO_LOCATION = { x: 50, y: 130 }; // Type { x: number; y: number; }
FOO_LOCATION.x = 10;

// ✅ Use
const FOO_LOCATION = { x: 50, y: 130 } as const; // Type '{ readonly x: 50; readonly y: 130; }'
FOO_LOCATION.x = 10; // Error

Arrays

// ❌ Avoid
const BAR_LOCATION = [50, 130]; // Type number[]
BAR_LOCATION.push(10);

// ✅ Use
const BAR_LOCATION = [50, 130] as const; // Type 'readonly [10, 20]'
BAR_LOCATION.push(10); // Error

Template Literals

// ❌ Avoid
const RATE_LIMIT = 25;
const RATE_LIMIT_MESSAGE = `Max number of requests/min is ${RATE_LIMIT}.`; // Type string

// ✅ Use
const RATE_LIMIT = 25;
const RATE_LIMIT_MESSAGE = `Max number of requests/min is ${RATE_LIMIT}.` as const; // Type 'Rate limit exceeded! Max number of requests/min is 25.'


Enums & Const Assertion
Enums are discouraged in the TypeScript ecosystem due to their runtime cost and quirks.
The TypeScript documentation outlines several pitfalls, and recently introduced the --erasableSyntaxOnly flag to disable runtime-generating features like enums altogether.


📏 Rule
As rule of a thumb, prefer:

Literal types whenever possible.
Const assertion arrays when looping through values.
Const assertion objects when enumerating arbitrary values.
Examples:

Use literal types to avoid runtime objects and reduce bundle size.

// ❌ Avoid using enums as they increase the bundle size
enum UserRole {
  GUEST = 'guest',
  MODERATOR = 'moderator',
  ADMINISTRATOR = 'administrator',
}

// Transpiled JavaScript
('use strict');
var UserRole;
(function (UserRole) {
  UserRole['GUEST'] = 'guest';
  UserRole['MODERATOR'] = 'moderator';
  UserRole['ADMINISTRATOR'] = 'administrator';
})(UserRole || (UserRole = {}));

// ✅ Use literal types - Types are stripped during transpilation
type UserRole = 'guest' | 'moderator' | 'administrator';

const isGuest = (role: UserRole) => role === 'guest';

Use const assertion arrays when looping through values.

// ❌ Avoid using enums
enum USER_ROLES {
  guest = 'guest',
  moderator = 'moderator',
  administrator = 'administrator',
}

// ✅ Use const assertions arrays
const USER_ROLES = ['guest', 'moderator', 'administrator'] as const;
type UserRole = (typeof USER_ROLES)[number];

const seedDatabase = () => {
  USER_ROLES.forEach((role) => {
    db.roles.insert(role);
  }
}
const insert = (role: UserRole) => {...

const UsersRoleList = () => {
  return (
    <div>
      {USER_ROLES.map((role) => (
        <Item key={role} role={role} />
      ))}
    </div>
  );
};
const Item = ({ role }: { role: UserRole }) => {...

Use const assertion objects when enumerating arbitrary values.

// ❌ Avoid using enums
enum COLORS {
  primary = '#B33930',
  secondary = '#113A5C',
  brand = '#9C0E7D',
}

// ✅ Use const assertions objects
const COLORS = {
  primary: '#B33930',
  secondary: '#113A5C',
  brand: '#9C0E7D',
} as const;

type Colors = typeof COLORS;
type ColorKey = keyof Colors; // Type "primary" | "secondary" | "brand"
type ColorValue = Colors[ColorKey]; // Type "#B33930" | "#113A5C" | "#9C0E7D"

const setColor = (color: ColorValue) => {...

setColor(COLORS.primary);
setColor('#B33930');

Type Union & Boolean Flags
Embrace type unions, especially when type union options are mutually exclusive, instead multiple boolean flag variables.

Boolean flags have a tendency to accumulate over time, leading to confusing and error-prone code, since they hide the actual app state.

// ❌ Avoid introducing multiple boolean flag variables
const isPending, isProcessing, isConfirmed, isExpired;

// ✅ Use type union variable
type UserStatus = 'pending' | 'processing' | 'confirmed' | 'expired';
const userStatus: UserStatus;

When boolean flags are used and the number of possible states grows quickly, it often results in unhandled or ambiguous states. Instead, take advantage of discriminated unions to better manage and represent your application's state.

Null & Undefined
In TypeScript types null and undefined many times can be used interchangeably.
Strive to:

Use null to explicitly state it has no value - assignment, return function type etc.
Use undefined assignment when the value doesn't exist. E.g. exclude fields in form, request payload, database query (Prisma differentiation) etc.
Naming
Strive to keep naming conventions consistent and readable, with important context provided, because another person will maintain the code you have written.

Named Export
Named exports must be used to ensure that all imports follow a uniform pattern 
📏 Rule
This keeps variables, functions etc. names consistent across the entire codebase. Named exports have the benefit of erroring when import statements try to import something that hasn't been declared.

Naming Conventions
While it's often hard to find the best name, aim to optimize code for consistency and future readers by following these conventions:

Variables
Locals
Camel case
products, productsFiltered

Booleans
Prefixed with is, has etc.
isDisabled, hasProduct


📏 Rule
Constants
Capitalized

const FEATURED_PRODUCT_ID = '8f47d2a1-b13e-4d5a-a7d8-6ef1234';

Object & Array Constants

Singular, capitalized with const assertion.

const IDLE_ORDER = {
  pending: 'idle',
  fulfilled: true,
  error: 'Shipping Error',
} as const;

const DASHBOARD_ACCESS_ROLES = ['admin', 'editor', 'moderator'] as const;

If a type exists use Type-Safe Constants With Satisfies.

// Type OrderStatus is predefined (e.g. generated from database schema, API)
type OrderStatus = {
  pending: 'pending' | 'idle';
  fulfilled: boolean;
  error: string;
};

const IDLE_ORDER = {
  pending: 'idle',
  fulfilled: true,
  error: 'Shipping Error',
} as const satisfies OrderStatus;

// Type UserRole is predefined
type UserRole = 'admin' | 'editor' | 'moderator' | 'viewer' | 'guest';

const DASHBOARD_ACCESS_ROLES = ['admin', 'editor', 'moderator'] as const satisfies ReadonlyArray<UserRole>;


Functions
Camel case
filterProductsByType, formatCurrency

Types
Pascal case
OrderStatus, ProductItem


📏 Rule
Generics
A generic type parameter must start with the capital letter T followed by a descriptive name TRequest, TFooBar.

Key reasons and benefits:

Complex types often involve generics, where clear naming improves readability and maintainability.
Single letter generics like T, K, U are disallowed, the more parameters we introduce, the easier it is to mistake them.
Prefixing with T makes it immediately obvious that it's a generic type parameter, not a regular type.
A common scenario is when a generic parameter shadows an existing type due to having the same name e.g. <Request extends Request>

📏 Rule
// ❌ Avoid naming generic parameters with one letter
const createPair = <T, K extends string>(first: T, second: K): [T, K] => {
  return [first, second];
};
const pair = createPair(1, 'a');

// ✅ Use descriptive names starting with capital T
const createPair = <TFirst, TSecond extends string>(first: TFirst, second: TSecond): [TFirst, TSecond] => {
  return [first, second];
};
const pair = createPair(1, 'a');

// ❌ Avoid naming generic parameters without a prefix - which 'Request' is which?
const handle = <Request extends Request>(req: Request): void => {...

// ✅ Prefix generic parameter with capital T
const handle = <TRequest extends Request>(req: TRequest): void => {...


Abbreviations & Acronyms
Treat acronyms as whole words, with capitalized first letter only.

// ❌ Avoid
const FAQList = ['qa-1', 'qa-2'];
const generateUserURL(params) => {...}

// ✅ Use
const FaqList = ['qa-1', 'qa-2'];
const generateUserUrl(params) => {...}

In favor of readability, strive to avoid abbreviations, unless they are widely accepted and necessary.

// ❌ Avoid
const GetWin(params) => {...}

// ✅ Use
const GetWindow(params) => {...}

React Components
Pascal case
ProductItem, ProductsPage

Prop Types
React component name following "Props" postfix
[ComponentName]Props - ProductItemProps, ProductsPageProps

Callback Props
Event handler (callback) props are prefixed as on* - e.g. onClick.
Event handler implementation functions are prefixed as handle* - e.g. handleClick.


📏 Rule
// ❌ Avoid inconsistent callback prop naming
<Button click={actionClick} />
<MyComponent userSelectedOccurred={triggerUser} />

// ✅ Use prop prefix 'on*' and handler prefix 'handle*'
<Button onClick={handleClick} />
<MyComponent onUserSelected={handleUserSelected} />

React Hooks
Camel case, prefixed as 'use' 
📏 Rule
Symmetrically convention as [value, setValue] = useState() 
📏 Rule
// ❌ Avoid inconsistent useState hook naming
const [userName, setUser] = useState();
const [color, updateColor] = useState();
const [isActive, setActive] = useState();

// ✅ Use
const [name, setName] = useState();
const [color, setColor] = useState();
const [isActive, setIsActive] = useState();

Custom hook must always return an object

// ❌ Avoid
const [products, errors] = useGetProducts();
const [fontSizes] = useTheme();

// ✅ Use
const { products, errors } = useGetProducts();
const { fontSizes } = useTheme();

Comments
Comments can quickly become outdated, leading to confusion rather than clarity.

Favor expressive code over comments by using meaningful names and clear logic. Comments should primarily explain "why," not "what" or "how."

Use comments when:

The context or reasoning isn't obvious from the code alone (e.g. config files, workarounds)
Referencing related issues, PRs, or planned improvements
// ❌ Avoid
// convert to minutes
const m = s * 60;
// avg users per minute
const myAvg = u / m;

// ✅ Use - Prefer expressive code by naming things what they are
const SECONDS_IN_MINUTE = 60;
const minutes = seconds * SECONDS_IN_MINUTE;
const averageUsersPerMinute = noOfUsers / minutes;

// ✅ Use - Reference planned improvements
// TODO: Move filtering to the backend once API v2 is released.
// Issue/PR - https://github.com/foo/repo/pulls/55124
const filteredUsers = frontendFiltering(selectedUsers);

// ✅ Use - Add context to explain why
// Use Fourier transformation to minimize information loss - https://github.com/dntj/jsfft#usage
const frequencies = signal.FFT();

TSDoc Comments
TSDoc comments enhance code maintainability and developer experience by providing structured documentation that IDEs, TypeScript, and API tools (e.g., Swagger, OpenAPI, GraphQL) can interpret.

Use TSDoc comments when documenting APIs, libraries, configurations or reusable code.

/**
 * Configuration options for the Web3 SDK.
 */
export type Web3Config = {
  /** Ethereum network chain ID. */
  chainId: number;

  /**
   * Gas price strategy for transactions:
   * - `fast`: Higher fees, faster confirmation
   * - `standard`: Balanced
   * - `slow`: Lower fees, slower confirmation
   */
  gasPriceStrategy: 'fast' | 'standard' | 'slow';

  /** Maximum gas limit per transaction. */
  maxGasLimit?: number;

  /** Enables event listening for smart contract interactions. */
  enableEventListener?: boolean;
};

Source Organization
Code Collocation
Every application or package in monorepo has project files/folders organized and grouped by feature.
Collocate code as close as possible to where it's relevant.
Deep folder nesting should not represent an issue.
Imports
Import paths can be relative, starting with ./ or ../, or they can be absolute @common/utils.

To make import statements more readable and easier to understand:

Relative imports ./sortItems must be used when importing files within the same feature, that are 'close' to each other, which also allows moving feature around the codebase without introducing changes in these imports.
Absolute imports @common/utils must be used in all other cases.
All imports must be auto sorted by tooling e.g. prettier-plugin-sort-imports, eslint-plugin-import etc.
// ❌ Avoid
import { bar, foo } from '../../../../../../distant-folder';

// ✅ Use
import { locationApi } from '@api/locationApi';

import { foo } from '../../foo';
import { bar } from '../bar';
import { baz } from './baz';

Project Structure
Example frontend monorepo project, where every application has file/folder grouped by feature:

apps/
├─ product-manager/
│  ├─ common/
│  │  ├─ components/
│  │  │  ├─ Button/
│  │  │  ├─ ProductTitle/
│  │  │  ├─ ...
│  │  │  └─ index.tsx
│  │  ├─ consts/
│  │  │  ├─ paths.ts
│  │  │  └─ ...
│  │  ├─ hooks/
│  │  └─ types/
│  ├─ modules/
│  │  ├─ HomePage/
│  │  ├─ ProductAddPage/
│  │  ├─ ProductPage/
│  │  ├─ ProductsPage/
│  │  │  ├─ api/
│  │  │  │  └─ useGetProducts/
│  │  │  ├─ components/
│  │  │  │  ├─ ProductItem/
│  │  │  │  ├─ ProductsStatistics/
│  │  │  │  └─ ...
│  │  │  ├─ utils/
│  │  │  │  └─ filterProductsByType/
│  │  │  └─ index.tsx
│  │  ├─ ...
│  │  └─ index.tsx
│  ├─ eslint.config.mjs
│  ├─ package.json
│  └─ tsconfig.json
├─ warehouse/
├─ admin-dashboard/
└─ ...

modules folder is responsible for implementation of each individual page, where all custom features for that page are being implemented (components, hooks, utils functions etc.).
common folder is responsible for implementations that are truly used across application. Since it's a "global folder" it should be used sparingly.
If same component e.g. common/components/ProductTitle starts being used on more than one page, it shall be moved to common folder.
In case using frontend framework with file-system based router (e.g. Nextjs), pages folder serves only as a router, where its responsibility is to define routes (no business logic implementation).

Example backend project structure with file/folder grouped by feature:

product-manager/
├─ dist/
├── database/
│   ├── migrations/
│   │   ├── 20220102063048_create_accounts.ts
│   │   └── ...
│   └── seeders/
│       ├── 20221116042655-feeds.ts
│       └── ...
├─ docker/
├─ logs/
├─ scripts/
├─ src/
│  ├─ common/
│  │  ├─ consts/
│  │  ├─ middleware/
│  │  ├─ types/
│  │  └─ ...
│  ├─ dao/
│  │  ├─ user/
│  │  └─ ...
│  ├─ modules/
│  │   ├── admin/
│  │   │   ├── account/
│  │   │   │   ├── account.model.ts
│  │   │   │   ├── account.controller.ts
│  │   │   │   ├── account.route.ts
│  │   │   │   ├── account.service.ts
│  │   │   │   ├── account.validation.ts
│  │   │   │   ├── account.test.ts
│  │   │   │   └── index.ts
│  │   │   └── ...
│  │   ├── general/
│  │   │   ├── general.model.ts
│  │   │   ├── general.controller.ts
│  │   │   ├── general.route.ts
│  │   │   ├── general.service.ts
│  │   │   ├── general.validation.ts
│  │   │   ├── general.test.ts
│  │   │   └── index.ts
│  │   ├─ ...
│  │   └─ index.tsx
│  └─ ...
├─ ...
├─ eslint.config.mjs
├─ package.json
└─ tsconfig.json

Appendix - React
Since React components and hooks are also functions, respective function conventions applies.

Required & Optional Props
Strive to have majority of props required and use optional props sparingly.

Especially when creating new component for first/single use case majority of props should be required. When component starts covering more use cases, introduce optional props.
There are potential exceptions, where component API needs to implement optional props from the start (e.g. shared components covering multiple use cases, UI design system components - button isDisabled etc.)

If component/hook becomes to complex it probably should be broken into smaller pieces.
An exaggerated example where implementing 10 React components with 5 required props each, is better then implementing one "can do it all" component that accepts 50 optional props.

Props as Discriminated Type
When applicable, use discriminated types to eliminate optional props. This approach reduces complexity in the component API and ensures that only the required props are passed based on the specific use case.

// ❌ Avoid optional props as they increase complexity and ambiguity in component APIs
type StatusProps = {
  data?: Products;
  title?: string;
  time?: number;
  error?: string;
};

// ✅ Prefer required props. If optional props are unavoidable,
// use a discriminated union to represent distinct use cases with required props.
type StatusSuccess = {
  status: 'success';
  data: Products;
  title: string;
};

type StatusLoading = {
  status: 'loading';
  time: number;
};

type StatusError = {
  status: 'error';
  error: string;
};

// Discriminated union 'StatusProps' ensures predictable component props with no optionals
type StatusProps = StatusSuccess | StatusLoading | StatusError;

export const Status = (status: StatusProps) => {
  switch (props.status) {
    case 'success':
      return <div>Title {props.title}</div>;
    case 'loading':
      return <div>Loading {props.time}</div>;
    case 'error':
      return <div>Error {props.error}</div>;
  }
};

Props To State
In general avoid using props to state, since component will not update on prop changes. It can lead to bugs that are hard to track, with unintended side effects and difficulty testing.
When there is truly a use case for using prop in initial state, prop must be prefixed with initial (e.g. initialProduct, initialSort etc.)

// ❌ Avoid using props to state
type FooProps = {
  productName: string;
  userId: string;
};

export const Foo = ({ productName, userId }: FooProps) => {
  const [productName, setProductName] = useState(productName);
  ...

// ✅ Use prop prefix `initial`, when there is a rational use case for it
type FooProps = {
  initialProductName: string;
  userId: string;
};

export const Foo = ({ initialProductName, userId }: FooProps) => {
  const [productName, setProductName] = useState(initialProductName);
  ...

Props Type
// ❌ Avoid using React.FC type
type FooProps = {
  name: string;
  score: number;
};

export const Foo: React.FC<FooProps> = ({ name, score }) => {

// ✅ Use props argument with type
type FooProps = {
  name: string;
  score: number;
};

export const Foo = ({ name, score }: FooProps) => {...

Component Types
Container
All container components have postfix "Container" or "Page" [ComponentName]Container|Page. Use "Page" postfix to indicate component is an actual web page.
Each feature has a container component (AddUserContainer.tsx, EditProductContainer.tsx, ProductsPage.tsx etc.)
Includes business logic.
API integration.
Structure:
ProductsPage/
├─ api/
│  └─ useGetProducts/
├─ components/
│  └─ ProductItem/
├─ utils/
│  └─ filterProductsByType/
└─ index.tsx

UI - Feature
Representational components that are designed to fulfill feature requirements.
Nested inside container component folder.
Should follow functions conventions as much as possible.
No API integration.
Structure:
ProductItem/
├─ index.tsx
├─ ProductItem.stories.tsx
└─ ProductItem.test.tsx

UI - Design system
Global Reusable/shared components used throughout whole codebase.
Structure:
Button/
├─ index.tsx
├─ Button.stories.tsx
└─ Button.test.tsx

Store & Pass Data
Pass only the necessary props to child components rather than passing the entire object.

Utilize storing state in the URL, especially for filtering, sorting etc.

Don't sync URL state with local state.

Consider passing data simply through props, using the URL, or composing children. Use global state (Zustand, Context) as a last resort.

Use React compound components when components should belong and work together: menu, accordion,navigation, tabs, list, etc.
Always export compound components as:

// PriceList.tsx
const PriceListRoot = ({ children }) => <ul>{children}</ul>;
const PriceListItem = ({ title, amount }) => <li>Name: {name} - Amount: {amount}<li/>;

// ❌
export const PriceList = {
  Container: PriceListRoot,
  Item: PriceListItem,
};
// ❌
PriceList.Item = Item;
export default PriceList;

// ✅
export const PriceList = PriceListRoot as typeof PriceListRoot & {
  Item: typeof PriceListItem;
};
PriceList.Item = PriceListItem;

// App.tsx
import { PriceList } from "./PriceList";

<PriceList>
  <PriceList.Item title="Item 1" amount={8} />
  <PriceList.Item title="Item 2" amount={12} />
</PriceList>;

UI components should show derived state and send events, nothing more (no business logic).

As in many programming languages functions args can be passed to the next function and on to the next etc.
React components are no different, where prop drilling should not become an issue.
If with app scaling prop drilling truly becomes an issue, try to refactor render method, local states in parent components, using composition etc.

Data fetching is only allowed in container components.

Use of server-state library is encouraged (react-query, apollo client etc.).

Use of client-state library for global state is discouraged.
Reconsider if something should be truly global across application, e.g. themeMode, Permissions or even that can be put in server-state (e.g. user settings - /me endpoint). If still global state is truly needed use Zustand or Context.

Appendix - Tests
What & How To Test
Automated test comes with benefits that helps us write better code and makes it easy to refactor, while bugs are caught earlier in the process.
Consider trade-offs of what and how to test to achieve confidence application is working as intended, while writing and maintaining tests doesn't slow the team down.

✅ Do:

Implement test to be short, explicit, and pleasant to work with. Intent of a test should be immediately visible.
Strive for AAA pattern, to maintain clean, organized, and understandable unit tests.
Arrange - Setup preconditions or the initial state necessary for the test case. Create necessary objects and define input values.
Act - Perform the action you want to unit test (invoke a method, triggering an event etc.). Strive for minimal number of actions.
Assert - Validate the outcome against expectations. Strive for minimal number of asserts.
A rule "unit tests should fail for exactly one reason" doesn't need to apply always, but it can indicate a code smell if there are tests with many asserts in a codebase.
As mentioned in function conventions try to keep them pure, and impure one small and focused.
It makes them easy to test, by passing args and observing return values, since we will rarely need to mock dependencies.
Strive to write tests in a way your app is used by a user, meaning test business logic.
E.g. For a specific user role or permission, given some input, we receive the expected output from the process.
Make tests as isolated as possible, where they don't depend on order of execution and should run independently with its own local storage, session storage, data, cookies etc. Test isolation speeds up the test run, improves reproducibility, makes debugging easier and prevents cascading test failures.
Tests should be resilient to changes.
Black box testing - Always test only implementation that is publicly exposed, don't write fragile tests on how implementation works internally.
Query HTML elements based on attributes that are unlikely to change. Order of priority must be followed as specified in Testing Library - role, label, placeholder, text contents, display value, alt text, title, test ID.
If testing with a database then make sure you control the data. If test are run against a staging environment make sure it doesn't change.
❌ Don't:

Don't test implementation details. When refactoring code, tests shouldn't change.

Don't re-test the library/framework.

Don't mandate 100% code coverage for applications.

Don't test third-party dependencies. Only test what your team controls (package, API, microservice etc.). Don't test external sites links, third party servers, packages etc.

Don't test just to test.

// ❌ Avoid
it('should render the user list', () => {
  render(<UserList />);
  expect(screen.getByText('Users List')).toBeInTheDocument();
});

Test Description
All test descriptions must follow naming convention as it('should ... when ...').


📏 Rule
// ❌ Avoid
it('accepts ISO date format where date is parsed and formatted as YYYY-MM');
it('after title is confirmed user description is rendered');

// ✅ Name test description as it('should ... when ...')
it('should return parsed date as YYYY-MM when input is in ISO date format');
it('should render user description when title is confirmed');

Test Tooling
Besides running tests through scripts, it's highly encouraged to use Vitest Runner and Playwright Test VS code extension alongside.
With extension any single unit/integration or E2E test can be run instantly, especially if testing app or package in larger monorepo codebase.

code --install-extension vitest.explorer
code --install-extension ms-playwright.playwright

Snapshot
Snapshot tests are discouraged to avoid fragility, which leads to a "just update it" mindset to make all tests pass.
Exceptions can be made, with strong rationale behind them, where test output has short and clear intent about what's actually being tested (e.g., design system library critical elements that shouldn't deviate).

---

## Verified References (official docs)

- TypeScript Handbook – Everyday Types and Narrowing
  - Everyday Types: https://www.typescriptlang.org/docs/handbook/2/everyday-types.html
  - Narrowing: https://www.typescriptlang.org/docs/handbook/2/narrowing.html
- Type Aliases vs Interfaces (guidance and differences)
  - https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#type-aliases
  - https://www.typescriptlang.org/docs/handbook/2/objects.html#interfaces
  - https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#differences-between-type-aliases-and-interfaces
- `unknown` (safer alternative to `any`)
  - https://www.typescriptlang.org/docs/handbook/2/unknown.html
- Readonly and immutability helpers
  - ReadonlyArray and `readonly` tuples: https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#readonlyarray
- `satisfies` operator (shape checking without widening)
  - https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html#the-satisfies-operator
- Enums and enum alternatives (`as const`, objects vs enums)
  - https://www.typescriptlang.org/docs/handbook/enums.html
  - https://www.typescriptlang.org/docs/handbook/enums.html#objects-vs-enums
- Utility Types
  - https://www.typescriptlang.org/docs/handbook/utility-types.html
- tsconfig options mentioned above
  - `exactOptionalPropertyTypes`: https://www.typescriptlang.org/tsconfig#exactOptionalPropertyTypes
  - `noUncheckedIndexedAccess`: https://www.typescriptlang.org/tsconfig#noUncheckedIndexedAccess
  - `noImplicitOverride`: https://www.typescriptlang.org/tsconfig#noImplicitOverride
  - `verbatimModuleSyntax`: https://www.typescriptlang.org/tsconfig#verbatimModuleSyntax
  - Module Resolution: https://www.typescriptlang.org/docs/handbook/module-resolution.html
- Linting (typescript-eslint, Flat Config)
  - https://typescript-eslint.io/getting-started/
