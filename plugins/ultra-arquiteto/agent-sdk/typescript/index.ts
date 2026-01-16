/**
 * Ultra Arquiteto - Claude Agent SDK Implementation (TypeScript)
 *
 * Sistema especialista em criacao de plugins para Claude Code e Claude Agent SDK.
 * Gera sistemas completos de agentes, skills, workflows, tools e commands.
 */

import Anthropic from "@anthropic-ai/sdk";
import * as fs from "fs";
import * as path from "path";

// =============================================================================
// TYPES
// =============================================================================

interface AgentDefinition {
  name: string;
  description: string;
  persona: string;
  principles?: string[];
  tools?: string[];
  guardrails?: string[];
}

interface SkillDefinition {
  name: string;
  description: string;
  triggers?: string[];
  phases?: Array<{ name: string; description: string }>;
}

interface WorkflowStep {
  name: string;
  agent: string;
  action: string;
  depends_on?: string[];
}

interface WorkflowDefinition {
  name: string;
  description: string;
  steps: WorkflowStep[];
}

interface ToolDefinition {
  name: string;
  description: string;
  parameters: Record<string, string>;
  implementation?: string;
}

interface CommandDefinition {
  name: string;
  description: string;
  trigger?: string;
  instructions: string;
}

interface PluginComponents {
  agents?: AgentDefinition[];
  skills?: SkillDefinition[];
  workflows?: WorkflowDefinition[];
  tools?: ToolDefinition[];
  commands?: CommandDefinition[];
}

// =============================================================================
// CONFIGURATION
// =============================================================================

const OUTPUT_DIR = "./_output";

function ensureDir(dirPath: string): void {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

// =============================================================================
// GENERATORS
// =============================================================================

export function createAgent(
  agent: AgentDefinition,
  format: "claude_code" | "agent_sdk" = "claude_code"
): string {
  const {
    name,
    description,
    persona,
    principles = [],
    tools = ["Read", "Write", "Edit"],
    guardrails = [],
  } = agent;

  if (format === "claude_code") {
    const content = `---
name: ${name}
description: ${description}
tools: ${tools.join(", ")}
model: sonnet
---

<persona>
${persona}
</persona>

<principles>
${principles.map((p, i) => `${i + 1}. ${p}`).join("\n")}
</principles>

<guardrails>
${guardrails.map((g) => `- ${g}`).join("\n")}
</guardrails>
`;

    const outputPath = path.join(OUTPUT_DIR, "claude-code", "agents", `${name}.md`);
    ensureDir(path.dirname(outputPath));
    fs.writeFileSync(outputPath, content, "utf-8");
    return outputPath;
  } else {
    const className = name
      .split("-")
      .map((s) => s.charAt(0).toUpperCase() + s.slice(1))
      .join("");

    const content = `/**
 * Agent: ${name}
 * ${description}
 */

export interface ${className}AgentConfig {
  name: string;
  description: string;
  persona: string;
  principles: string[];
  guardrails: string[];
  tools: string[];
}

export class ${className}Agent {
  readonly name = "${name}";
  readonly description = "${description}";
  readonly persona = \`${persona}\`;
  readonly principles = ${JSON.stringify(principles, null, 2)};
  readonly guardrails = ${JSON.stringify(guardrails, null, 2)};
  readonly tools = ${JSON.stringify(tools, null, 2)};

  async execute(task: string): Promise<Record<string, unknown>> {
    // Implementation here
    return { status: "ok", task };
  }
}
`;

    const outputPath = path.join(
      OUTPUT_DIR,
      "agent-sdk",
      "typescript",
      "agents",
      `${name.replace(/-/g, "_")}.ts`
    );
    ensureDir(path.dirname(outputPath));
    fs.writeFileSync(outputPath, content, "utf-8");
    return outputPath;
  }
}

export function createSkill(
  skill: SkillDefinition,
  format: "claude_code" | "agent_sdk" = "claude_code"
): string {
  const { name, description, triggers = [], phases = [] } = skill;

  if (format === "claude_code") {
    const content = `# ${name}

${description}

## Triggers

${triggers.map((t) => `- ${t}`).join("\n")}

## Phases

${phases.map((p, i) => `### Phase ${i + 1}: ${p.name}\n${p.description}`).join("\n\n")}
`;

    const outputPath = path.join(OUTPUT_DIR, "claude-code", "skills", name, "SKILL.md");
    ensureDir(path.dirname(outputPath));
    fs.writeFileSync(outputPath, content, "utf-8");
    return outputPath;
  } else {
    const className = name
      .split("-")
      .map((s) => s.charAt(0).toUpperCase() + s.slice(1))
      .join("");

    const content = `/**
 * Skill: ${name}
 * ${description}
 */

export class ${className}Skill {
  readonly name = "${name}";
  readonly triggers = ${JSON.stringify(triggers, null, 2)};
  readonly phases = ${JSON.stringify(phases.map((p) => p.name), null, 2)};

  async execute(context: Record<string, unknown>): Promise<Record<string, unknown>> {
    const results: Record<string, unknown> = {};
    for (const phase of this.phases) {
      results[phase] = await this.executePhase(phase, context);
    }
    return results;
  }

  private async executePhase(
    phase: string,
    context: Record<string, unknown>
  ): Promise<unknown> {
    // Phase implementation
    return { phase, status: "completed" };
  }
}
`;

    const outputPath = path.join(
      OUTPUT_DIR,
      "agent-sdk",
      "typescript",
      "skills",
      `${name.replace(/-/g, "_")}.ts`
    );
    ensureDir(path.dirname(outputPath));
    fs.writeFileSync(outputPath, content, "utf-8");
    return outputPath;
  }
}

export function createWorkflow(
  workflow: WorkflowDefinition,
  format: "claude_code" | "agent_sdk" = "claude_code"
): string {
  const { name, description, steps } = workflow;

  if (format === "claude_code") {
    const content = `# Workflow: ${name}

${description}

## Steps

${steps
  .map(
    (s, i) => `### Step ${i + 1}: ${s.name}
- Agent: ${s.agent}
- Action: ${s.action}
- Depends on: ${s.depends_on?.join(", ") || "None"}
`
  )
  .join("\n")}
`;

    const outputPath = path.join(OUTPUT_DIR, "claude-code", "workflows", `${name}.md`);
    ensureDir(path.dirname(outputPath));
    fs.writeFileSync(outputPath, content, "utf-8");
    return outputPath;
  } else {
    const className = name
      .split("-")
      .map((s) => s.charAt(0).toUpperCase() + s.slice(1))
      .join("");

    const content = `/**
 * Workflow: ${name}
 * ${description}
 */

export interface WorkflowStep {
  name: string;
  agent: string;
  action: string;
  depends_on?: string[];
}

export class ${className}Workflow {
  readonly name = "${name}";
  readonly steps: WorkflowStep[] = ${JSON.stringify(steps, null, 2)};

  async execute(context: Record<string, unknown>): Promise<Record<string, unknown>> {
    const results: Record<string, unknown> = {};

    for (const step of this.steps) {
      const depsMet = (step.depends_on || []).every((d) => d in results);
      if (depsMet) {
        results[step.name] = await this.executeStep(step, context, results);
      }
    }

    return results;
  }

  private async executeStep(
    step: WorkflowStep,
    context: Record<string, unknown>,
    priorResults: Record<string, unknown>
  ): Promise<unknown> {
    // Step implementation
    return { step: step.name, status: "completed" };
  }
}
`;

    const outputPath = path.join(
      OUTPUT_DIR,
      "agent-sdk",
      "typescript",
      "workflows",
      `${name.replace(/-/g, "_")}.ts`
    );
    ensureDir(path.dirname(outputPath));
    fs.writeFileSync(outputPath, content, "utf-8");
    return outputPath;
  }
}

export function createTool(tool: ToolDefinition): string {
  const { name, description, parameters, implementation = "// TODO" } = tool;

  const paramsType = Object.entries(parameters)
    .map(([k, v]) => `${k}: ${v}`)
    .join("; ");

  const content = `/**
 * Tool: ${name}
 * ${description}
 */

export interface ${name
    .split("-")
    .map((s) => s.charAt(0).toUpperCase() + s.slice(1))
    .join("")}Args {
  ${paramsType}
}

export async function ${name.replace(/-/g, "_")}(
  args: ${name
    .split("-")
    .map((s) => s.charAt(0).toUpperCase() + s.slice(1))
    .join("")}Args
): Promise<{ content: Array<{ type: string; text: string }> }> {
  ${implementation}

  return {
    content: [{ type: "text", text: JSON.stringify({ status: "ok" }) }],
  };
}
`;

  const outputPath = path.join(
    OUTPUT_DIR,
    "agent-sdk",
    "typescript",
    "tools",
    `${name.replace(/-/g, "_")}.ts`
  );
  ensureDir(path.dirname(outputPath));
  fs.writeFileSync(outputPath, content, "utf-8");
  return outputPath;
}

export function createCommand(command: CommandDefinition): string {
  const { name, description, trigger = `/${name}`, instructions } = command;

  const content = `---
name: ${name}
description: ${description}
trigger: ${trigger}
---

# /${name}

${description}

## Instructions

${instructions}
`;

  const outputPath = path.join(OUTPUT_DIR, "claude-code", "commands", `${name}.md`);
  ensureDir(path.dirname(outputPath));
  fs.writeFileSync(outputPath, content, "utf-8");
  return outputPath;
}

// =============================================================================
// PLUGIN GENERATOR
// =============================================================================

export function generatePlugin(
  pluginName: string,
  description: string,
  components: PluginComponents
): Record<string, string[]> {
  const results: Record<string, string[]> = {
    agents: [],
    skills: [],
    workflows: [],
    tools: [],
    commands: [],
  };

  // Generate agents
  for (const agent of components.agents || []) {
    results.agents.push(createAgent(agent, "claude_code"));
    results.agents.push(createAgent(agent, "agent_sdk"));
  }

  // Generate skills
  for (const skill of components.skills || []) {
    results.skills.push(createSkill(skill, "claude_code"));
    results.skills.push(createSkill(skill, "agent_sdk"));
  }

  // Generate workflows
  for (const workflow of components.workflows || []) {
    results.workflows.push(createWorkflow(workflow, "claude_code"));
    results.workflows.push(createWorkflow(workflow, "agent_sdk"));
  }

  // Generate tools
  for (const tool of components.tools || []) {
    results.tools.push(createTool(tool));
  }

  // Generate commands
  for (const command of components.commands || []) {
    results.commands.push(createCommand(command));
  }

  console.log(`Plugin "${pluginName}" generated successfully!`);
  console.log(`Description: ${description}`);
  console.log(`Generated files:`, results);

  return results;
}

// =============================================================================
// CLI
// =============================================================================

if (require.main === module) {
  console.log("Ultra Arquiteto - Plugin Generator (TypeScript)");
  console.log("Usage: npx ts-node index.ts");
}
