import eslint from "@eslint/js";
import nextPlugin from "@next/eslint-plugin-next";
import globals from "globals";
import tseslint from "typescript-eslint";

export default tseslint.config(
  {
    ignores: [".next/**", "node_modules/**", "coverage/**"],
  },
  eslint.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ["**/*.{js,mjs,cjs,ts,tsx}"],
    languageOptions: {
      globals: globals.browser,
    },
    plugins: {
      "@next/next": nextPlugin,
    },
    rules: {
      ...nextPlugin.configs.recommended.rules,
    },
  },
);
