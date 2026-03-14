---
name: ue5-puerts-init-skill
description: Initialize Puerts (JavaScript/TypeScript runtime) plugin in Unreal Engine 5 projects. Use this skill when setting up a new UE5 project with JavaScript/TypeScript support, integrating Puerts plugin, or when the user mentions "add Puerts", "setup Puerts in UE", "enable Puerts in Unreal", "configure Puerts", or needs to set up the TypeScript runtime for UE5. This skill handles the complete setup workflow with plugin installation, C++ GameInstance configuration, TypeScript environment setup, and type definitions. Always use this skill when starting a new UE5 project that needs Puerts support or when the user asks about integrating Puerts with Unreal Engine.
---

# UE5 Puerts Initialization

This skill guides through the complete setup of Puerts (JavaScript/TypeScript runtime) for Unreal Engine 5 projects.

## Overview

Puerts enables writing UE5 gameplay code in JavaScript/TypeScript with full access to UE APIs.

The setup involves:
1. Installing the Puerts plugin and V8 engine
2. Configuring C++ module dependencies
3. Creating a GameInstance to initialize the JavaScript runtime
4. Setting up the TypeScript compilation environment
5. Compiling TypeScript and verifying the setup

Execute each phase in order. The "Continue to: Phase X" anchors guide you to the next step.

---

## Phase 1: Install Puerts Plugin

Run the installation script from your project root:

```bash
cd [ProjectRoot]
python scripts/install_puerts.py
```

This script:
- Clones the Puerts repository
- Copies the plugin to `Plugins/Puerts/`
- Downloads V8 9.4.146.24 engine
- Extracts to `ThirdParty/v8_9.4.146.24/`
- Cleans up temporary files

**Verify:**
```bash
ls Plugins/Puerts/Source/
ls Plugins/Puerts/ThirdParty/v8_9.4.146.24/Inc/v8.h
```

**Completion:** The plugin directory exists with all source files and V8 headers.

Continue to: Phase 2

---

## Phase 2: Configure C++ Module Dependencies

Edit your project's Build.cs file at `Source/[ProjectName]/[ProjectName].Build.cs`.

Add `"JsEnv"` and `"Puerts"` to `PublicDependencyModuleNames`:

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core", "CoreUObject", "Engine", "InputCore", "JsEnv", "Puerts"
});
```

**Why:** This tells Unreal's build system to link against the Puerts JavaScript runtime modules.

**Verify:**
```bash
grep "JsEnv\|Puerts" Source/[ProjectName]/[ProjectName].Build.cs
```

**Completion:** Build.cs contains both `JsEnv` and `Puerts`.

Continue to: Phase 3

---

## Phase 3: Create GameInstance

The GameInstance initializes the JavaScript runtime when the game starts.

### Step 3.1: Run Configuration Script

```bash
python scripts/replace_api_macro.py
```

This script:
1. Creates `Public/` and `Private/` directories if they don't exist
2. Copies MyGameInstance template files to your project source
3. Detects your project name from the .uproject file
4. Replaces `YOURPROJECT_API` placeholder in MyGameInstance.h
5. Configures `GameInstanceClass` in `Config/DefaultEngine.ini`
6. Copies minimal TypeScript type definitions to `Typing/`
7. Backs up the original config file

**Why:** The GameInstance is the entry point for JavaScript execution. It loads `Main.ts` when the game starts.

**Verify:**
```bash
grep "[ProjectName]_API" Source/[ProjectName]/Public/MyGameInstance.h
grep "MyGameInstance" Config/DefaultEngine.ini
ls Typing/puerts/index.d.ts
ls Typing/ue/puerts.d.ts
```

**Completion:** API macro replaced, GameInstance configured, type definitions copied.

Continue to: Phase 4

---

## Phase 4: Setup TypeScript Environment

### Step 4.1: Create Directory

```bash
mkdir -p Typescript
```

### Step 4.2: Copy Template Files

```bash
cp assets/package.json Typescript/
cp assets/tsconfig.json Typescript/
cp assets/global.d.ts Typescript/
cp assets/Main.ts Typescript/
```

### Step 4.3: Install Dependencies

```bash
cd Typescript
npm install
```

**About Type Definitions:**

Type definitions were already copied to `Typing/` in Phase 3. These include:

- **puerts/** - Core Puerts APIs (argv object, blueprint functions, etc.)
- **ue/** - Minimal UE type definitions (Object, Class, container types)

These are minimal type definitions (~10KB) sufficient for basic functionality. They're cross-project and cross-version compatible.

**Verify:**
```bash
ls Typescript/node_modules/
```

**Completion:** npm dependencies installed.

Continue to: Phase 5

---

## Phase 5: Compile and Run

### Step 5.1: Compile TypeScript

```bash
cd Typescript
npm run build
```

This compiles `Main.ts` to `Content/JavaScript/Main.js`.

**Verify:**
```bash
ls Content/JavaScript/Main.js
```

**Completion:** Main.js exists in Content/JavaScript/.

Continue to: Step 5.2

---

### Step 5.2: Run and Verify

1. Open your project in the UE Editor (will automatically compile C++ code)
2. Click the **Play** button
3. Check the Output Log

**Success Criteria:**

You should see this in the output log:

```
========================================
Puerts TypeScript Loaded Successfully!
GameInstance: [object]
========================================
```

**Setup Complete!** If you see the message above, Puerts is successfully integrated.

---

## Troubleshooting

### TypeScript compilation fails with "Cannot find module 'ue'"

Ensure:
1. Type definitions were copied in Phase 3 (check `Typing/` directory exists)
2. `global.d.ts` exists in `Typescript/`
3. `tsconfig.json` has correct `typeRoots` configuration

### No TypeScript log output when running

Check:
1. `GameInstanceClass` is configured in `Config/DefaultEngine.ini`
2. C++ code compiled (UE Editor shows no compilation errors)
3. TypeScript compiled to JavaScript (Main.js exists in Content/JavaScript/)
4. Check Output Log for error messages

### TypeScript changes don't update in game

1. Recompile TypeScript: `cd Typescript && npm run build`
2. Stop PIE mode and restart
3. Some changes require restart (Puerts supports hot reload for most cases)

### Type definitions seem incomplete

The minimal type definitions are sufficient for basic functionality. For complete IDE autocomplete, generate full type definitions in UE Editor: `Tools` → `Puerts` → `Generate TypeScript Declarations`

---

## File Structure

```
Project/
├── Source/[ProjectName]/
│   ├── Public/MyGameInstance.h
│   └── Private/MyGameInstance.cpp
├── Content/JavaScript/Main.js (compiled from TypeScript)
├── Typescript/
│   ├── package.json
│   ├── tsconfig.json
│   ├── global.d.ts
│   ├── Main.ts
│   └── node_modules/
├── Typing/
│   ├── puerts/ (minimal type definitions)
│   └── ue/ (minimal type definitions)
├── Config/DefaultEngine.ini
└── Plugins/Puerts/
```

---

## Debugging JavaScript

### Enable Debugger

In `MyGameInstance.cpp`, uncomment in `OnStart()`:

```cpp
GameScript->WaitDebugger();
```

### Connect Chrome DevTools

1. Open `chrome://inspect` in Chrome
2. Click "inspect" to connect to the debugging session
3. Set breakpoints, inspect variables, view call stacks

---

## Next Steps

After integration:

1. Write TypeScript code in `Typescript/`
2. Use decorators like `@uclass`, `@uproperty` to extend UE classes
3. Call C++ from JavaScript via imported UE types
4. Use React-UMG for UI development
