# Commit Change Command

This command commits the current changes in your working directory with an AI-generated commit message.

## Usage

The commit-change command will:
- Analyze the staged and unstaged changes in your repository
- Generate a descriptive commit message based on the changes
- Create a commit with the generated message

## When to Use

- After making code changes and you want a well-crafted commit message
- When you want to quickly commit without manually writing a message
- For maintaining consistent commit message quality across your project

## Prerequisites

- Have changes staged or unstaged in your git repository
- Be in a git repository directory
- Have git configured with user name and email

## Examples

- `@commit-change` - Commits all current changes with AI-generated message
- Works with both staged and unstaged changes
- Automatically detects the type of changes (features, fixes, refactoring, etc.)

## Notes

- The AI will analyze your changes and create an appropriate commit message
- Review the generated message before confirming the commit
- The command respects git's staging area - staged changes will be committed 