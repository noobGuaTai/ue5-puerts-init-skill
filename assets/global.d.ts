/// <reference path="../Typing/ue/index.d.ts" />
/// <reference path="../Typing/puerts/index.d.ts" />

// Declare "ue" module
declare module "ue" {
    export * from "ue";
}

// Declare "puerts" module
declare module "puerts" {
    export * from "puerts";
}

// Declare Global console (Provided by the V8 engine)
declare const console: {
    log(...args: any[]): void;
    error(...args: any[]): void;
    warn(...args: any[]): void;
    info(...args: any[]): void;
};
