# Opal Safe Code Generator - Frontend

React + TypeScript frontend dashboard for the Opal Safe Code Generator.

## Tech Stack

- **React 18** with TypeScript
- **Vite** - Build tool and dev server
- **TanStack Query** - API state management
- **React Router** - Routing
- **shadcn/ui** - UI component library
- **Tailwind CSS** - Styling
- **Monaco Editor** - Code editor for templates and rules
- **React Hook Form + Zod** - Form handling and validation
- **Axios** - HTTP client

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## Build

```bash
npm run build
```

## Features

- **Brands CRUD** - Manage brands and their configurations
- **Templates CRUD** - Manage code templates with Monaco editor
- **Selectors CRUD** - Manage DOM selectors for page targeting
- **Rules CRUD** - Manage validation rules with Monaco editor
- **Generated Code** - Read-only view of generated code entries

## API Configuration

The frontend is configured to connect to the backend at `http://localhost:8000/api/v1`.

The Vite proxy is configured to forward `/api` requests to the backend during development.

