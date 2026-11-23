// Entry point for Meme Sprint 3: AI Agent Goes Rogue.
// Copies the pre-rendered entry.png into the output directory.
// Node 22, standard library only. Never deletes the output dir.
import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "entry.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";

if (!existsSync(source)) {
  console.error("entry.png missing next to main.ts");
  process.exit(1);
}

mkdirSync(outDir, { recursive: true });
copyFileSync(source, join(outDir, "entry.png"));
console.log("entry.png written to " + outDir);
