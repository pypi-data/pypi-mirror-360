# Create a Modern Web App

When using AI tools like synth.codeai to create a modern web application, it's most effective to break down the work from a high level into discrete tasks. This guide will walk you through a practical example of building a Next.js application with common modern features.

## Setting Up a Fresh Next.js Application

To get started with a new Next.js project, you can use synth.codeai with a simple command like:

```
synth-codeai -m "Initialize a new nextjs app."
```

synth.codeai will execute the necessary commands and set up a clean Next.js project for you with the latest best practices. It'll even search the web to read documentation about the latest version of Next.

## Adding shadcn/ui Components

Once your base Next.js application is ready, you can add the shadcn/ui component library. Tell synth.codeai:

```
synth-codeai -m "Install shadcn into this project and put a few examples of shadcn components on the main page."
```

This will configure your project with shadcn/ui's CLI, set up the necessary styling, and add your first components.

## Integrating Prisma with SQLite

For database integration, you can add Prisma ORM with SQLite. Simply instruct synth.codeai:

```
synth-codeai -m "Integrate prisma/sqlite into this project."
```

synth.codeai will handle the Prisma setup, create your database schema, and set up your first model.

## Adding Features Incrementally

With the foundation in place, you can start adding features one by one. Here's an example:

```
synth-codeai -m "Add a simple user registration form. Include fields for email and password."
```

Keep your feature requests focused and specific. This allows synth.codeai to implement them effectively while maintaining code quality.

Remember to build your application incrementally, testing each feature as it's added. This approach helps manage complexity and ensures a stable development process.