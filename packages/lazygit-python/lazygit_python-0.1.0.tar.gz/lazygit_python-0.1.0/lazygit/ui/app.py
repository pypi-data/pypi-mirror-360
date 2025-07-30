from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Tree, Static, Input, TextArea, ListView, ListItem, Label, DataTable
from textual.widget import Widget
from textual.binding import Binding
from textual.reactive import reactive
from textual.message import Message
from textual import events
from textual.screen import Screen
from typing import Optional, List, Dict
import os
from datetime import datetime

from ..git_operations import GitOperations
from ..config import Config
from .dialogs import InputDialog, ConfirmDialog, StashDialog


class FileStatus(ListItem):
    def __init__(self, file_info: Dict[str, str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_info = file_info
        
    def compose(self) -> ComposeResult:
        status_map = {
            'M': '✏️  Modified',
            'A': '➕ Added',
            'D': '➖ Deleted',
            'R': '➡️  Renamed',
            'C': '📋 Copied',
            'U': '⚠️  Updated'
        }
        status = status_map.get(self.file_info['change_type'], '❓ Unknown')
        yield Label(f"{status}: {self.file_info['path']}")


class BranchItem(ListItem):
    def __init__(self, branch_info: Dict[str, any], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.branch_info = branch_info
        
    def compose(self) -> ComposeResult:
        prefix = "* " if self.branch_info['is_current'] else "  "
        remote_indicator = " (remote)" if self.branch_info.get('is_remote', False) else ""
        yield Label(f"{prefix}{self.branch_info['name']}{remote_indicator} - {self.branch_info['commit']}")


class CommitItem(ListItem):
    def __init__(self, commit_info: Dict[str, any], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.commit_info = commit_info
        
    def compose(self) -> ComposeResult:
        yield Label(f"{self.commit_info['sha']} - {self.commit_info['message']}")


class CommitMessageScreen(Screen):
    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("escape", "cancel", "Cancel"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static("Enter commit message:", id="commit-prompt"),
            TextArea(id="commit-message"),
            id="commit-dialog"
        )
    
    def on_mount(self) -> None:
        self.query_one("#commit-message").focus()
    
    def action_save(self) -> None:
        message = self.query_one("#commit-message", TextArea).text
        if message.strip():
            self.dismiss(message.strip())
    
    def action_cancel(self) -> None:
        self.dismiss(None)


class DiffViewer(Screen):
    BINDINGS = [
        Binding("escape", "close", "Close"),
    ]
    
    def __init__(self, diff_content: str, title: str = "Diff", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.diff_content = diff_content
        self.title = title
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static(self.title, id="diff-title"),
            ScrollableContainer(
                Static(self.diff_content, id="diff-content"),
                id="diff-scroll"
            ),
            id="diff-viewer"
        )
    
    def action_close(self) -> None:
        self.dismiss()


class LazyGitApp(App):
    CSS = """
    #main-container {
        layout: grid;
        grid-size: 2 2;
        grid-rows: 1fr 1fr;
        grid-columns: 1fr 1fr;
    }
    
    #status-panel {
        border: solid green;
        overflow-y: auto;
    }
    
    #files-panel {
        border: solid blue;
        overflow-y: auto;
    }
    
    #branches-panel {
        border: solid yellow;
        overflow-y: auto;
    }
    
    #commits-panel {
        border: solid magenta;
        overflow-y: auto;
    }
    
    #commit-dialog, #input-dialog, #confirm-dialog, #stash-dialog {
        align: center middle;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
        width: 60;
        height: 10;
    }
    
    #commit-message {
        width: 100%;
        height: 5;
    }
    
    #diff-viewer {
        width: 80%;
        height: 80%;
        background: $surface;
        border: thick $primary;
        align: center middle;
    }
    
    #diff-scroll {
        width: 100%;
        height: 1fr;
        overflow-y: auto;
    }
    
    #diff-title {
        background: $primary;
        color: $text;
        padding: 0 1;
        text-style: bold;
    }
    
    .panel-title {
        background: $primary;
        color: $text;
        padding: 0 1;
        text-style: bold;
    }
    
    ListView {
        height: 100%;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("s", "stage_toggle", "Stage/Unstage"),
        Binding("a", "stage_all", "Stage All"),
        Binding("u", "unstage_all", "Unstage All"),
        Binding("c", "commit", "Commit"),
        Binding("p", "push", "Push"),
        Binding("P", "pull", "Pull"),
        Binding("f", "fetch", "Fetch"),
        Binding("b", "checkout_branch", "Checkout Branch"),
        Binding("n", "new_branch", "New Branch"),
        Binding("d", "delete_branch", "Delete Branch"),
        Binding("S", "stash", "Stash"),
        Binding("ctrl+s", "stash_pop", "Stash Pop"),
        Binding("m", "merge", "Merge"),
        Binding("R", "rebase", "Rebase"),
        Binding("D", "diff", "View Diff"),
        Binding("enter", "show_commit", "Show Commit"),
        Binding("tab", "focus_next", "Next Panel"),
        Binding("shift+tab", "focus_previous", "Previous Panel"),
        Binding("?", "help", "Help"),
    ]
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.git_ops = GitOperations()
        self.current_panel = "files"
        self._setup_custom_bindings()
        
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Vertical(
                Static("📁 Files", classes="panel-title"),
                ListView(id="files-panel"),
                id="files-container"
            ),
            Vertical(
                Static("🌿 Branches", classes="panel-title"),
                ListView(id="branches-panel"),
                id="branches-container"
            ),
            Vertical(
                Static("📊 Status", classes="panel-title"),
                Static(id="status-panel"),
                id="status-container"
            ),
            Vertical(
                Static("📝 Commits", classes="panel-title"),
                ListView(id="commits-panel"),
                id="commits-container"
            ),
            id="main-container"
        )
        yield Footer()
    
    def on_mount(self) -> None:
        if not self.git_ops.is_git_repo():
            self.notify("Not a git repository!", severity="error")
            self.exit()
        else:
            self.refresh_all()
            self.query_one("#files-panel").focus()
    
    def refresh_all(self) -> None:
        self.refresh_status()
        self.refresh_files()
        self.refresh_branches()
        self.refresh_commits()
    
    def refresh_status(self) -> None:
        status_panel = self.query_one("#status-panel", Static)
        current_branch = self.git_ops.get_current_branch()
        remotes = self.git_ops.get_remotes()
        
        status_text = f"Branch: {current_branch}\n"
        if remotes:
            status_text += f"Remote: {remotes[0]['name']} ({remotes[0]['url']})\n"
        else:
            status_text += "Remote: None\n"
        
        status_panel.update(status_text)
    
    def refresh_files(self) -> None:
        files_panel = self.query_one("#files-panel", ListView)
        files_panel.clear()
        
        status = self.git_ops.get_status()
        
        if status['staged']:
            files_panel.append(ListItem(Label("── Staged Changes ──")))
            for file_info in status['staged']:
                files_panel.append(FileStatus(file_info))
        
        if status['unstaged']:
            if status['staged']:
                files_panel.append(ListItem(Label("")))
            files_panel.append(ListItem(Label("── Unstaged Changes ──")))
            for file_info in status['unstaged']:
                files_panel.append(FileStatus(file_info))
        
        if status['untracked']:
            if status['staged'] or status['unstaged']:
                files_panel.append(ListItem(Label("")))
            files_panel.append(ListItem(Label("── Untracked Files ──")))
            for file_info in status['untracked']:
                files_panel.append(FileStatus(file_info))
    
    def refresh_branches(self) -> None:
        branches_panel = self.query_one("#branches-panel", ListView)
        branches_panel.clear()
        
        branches = self.git_ops.get_branches()
        
        local_branches = [b for b in branches if not b.get('is_remote', False)]
        remote_branches = [b for b in branches if b.get('is_remote', False)]
        
        if local_branches:
            branches_panel.append(ListItem(Label("── Local Branches ──")))
            for branch in local_branches:
                branches_panel.append(BranchItem(branch))
        
        if remote_branches:
            if local_branches:
                branches_panel.append(ListItem(Label("")))
            branches_panel.append(ListItem(Label("── Remote Branches ──")))
            for branch in remote_branches:
                branches_panel.append(BranchItem(branch))
    
    def refresh_commits(self) -> None:
        commits_panel = self.query_one("#commits-panel", ListView)
        commits_panel.clear()
        
        commits = self.git_ops.get_commits(max_count=20)
        for commit in commits:
            commits_panel.append(CommitItem(commit))
    
    def action_refresh(self) -> None:
        self.refresh_all()
        self.notify("Refreshed")
    
    def action_stage_toggle(self) -> None:
        focused = self.focused
        if focused and isinstance(focused.parent, ListView) and focused.parent.id == "files-panel":
            if hasattr(focused, 'children') and focused.children:
                child = focused.children[0]
                if isinstance(child, FileStatus):
                    file_path = child.file_info['path']
                    status = self.git_ops.get_status()
                    
                    if any(f['path'] == file_path for f in status['staged']):
                        self.git_ops.unstage_file(file_path)
                        self.notify(f"Unstaged: {file_path}")
                    else:
                        self.git_ops.stage_file(file_path)
                        self.notify(f"Staged: {file_path}")
                    
                    self.refresh_files()
    
    def action_stage_all(self) -> None:
        self.git_ops.stage_all()
        self.notify("Staged all files")
        self.refresh_files()
    
    def action_unstage_all(self) -> None:
        self.git_ops.unstage_all()
        self.notify("Unstaged all files")
        self.refresh_files()
    
    async def action_commit(self) -> None:
        status = self.git_ops.get_status()
        if not status['staged']:
            self.notify("No staged changes to commit", severity="warning")
            return
        
        message = await self.push_screen(CommitMessageScreen())
        if message:
            try:
                self.git_ops.commit(message)
                self.notify(f"Committed: {message}")
                self.refresh_all()
            except Exception as e:
                self.notify(f"Commit failed: {str(e)}", severity="error")
    
    def action_push(self) -> None:
        try:
            self.git_ops.push()
            self.notify("Pushed successfully")
        except Exception as e:
            if "upstream" in str(e):
                try:
                    self.git_ops.push(set_upstream=True)
                    self.notify("Pushed with upstream set")
                except Exception as e2:
                    self.notify(f"Push failed: {str(e2)}", severity="error")
            else:
                self.notify(f"Push failed: {str(e)}", severity="error")
    
    def action_pull(self) -> None:
        try:
            self.git_ops.pull()
            self.notify("Pulled successfully")
            self.refresh_all()
        except Exception as e:
            self.notify(f"Pull failed: {str(e)}", severity="error")
    
    def action_fetch(self) -> None:
        try:
            self.git_ops.fetch()
            self.notify("Fetched successfully")
            self.refresh_branches()
        except Exception as e:
            self.notify(f"Fetch failed: {str(e)}", severity="error")
    
    def action_checkout_branch(self) -> None:
        focused = self.focused
        if focused and isinstance(focused.parent, ListView) and focused.parent.id == "branches-panel":
            if hasattr(focused, 'children') and focused.children:
                child = focused.children[0]
                if isinstance(child, BranchItem):
                    branch_name = child.branch_info['name']
                    if not child.branch_info['is_current']:
                        try:
                            self.git_ops.checkout_branch(branch_name)
                            self.notify(f"Checked out: {branch_name}")
                            self.refresh_all()
                        except Exception as e:
                            self.notify(f"Checkout failed: {str(e)}", severity="error")
    
    def action_focus_next(self) -> None:
        panels = ["#files-panel", "#branches-panel", "#commits-panel"]
        current_focus = self.focused
        
        current_index = -1
        for i, panel_id in enumerate(panels):
            panel = self.query_one(panel_id)
            if panel == current_focus or (current_focus and current_focus.parent == panel):
                current_index = i
                break
        
        next_index = (current_index + 1) % len(panels)
        self.query_one(panels[next_index]).focus()
    
    def action_focus_previous(self) -> None:
        panels = ["#files-panel", "#branches-panel", "#commits-panel"]
        current_focus = self.focused
        
        current_index = -1
        for i, panel_id in enumerate(panels):
            panel = self.query_one(panel_id)
            if panel == current_focus or (current_focus and current_focus.parent == panel):
                current_index = i
                break
        
        prev_index = (current_index - 1) % len(panels)
        self.query_one(panels[prev_index]).focus()
    
    async def action_new_branch(self) -> None:
        branch_name = await self.push_screen(InputDialog(
            "New Branch",
            "Enter branch name:",
            "feature/new-branch"
        ))
        
        if branch_name:
            try:
                self.git_ops.create_branch(branch_name)
                self.notify(f"Created and checked out branch: {branch_name}")
                self.refresh_all()
            except Exception as e:
                self.notify(f"Failed to create branch: {str(e)}", severity="error")
    
    async def action_delete_branch(self) -> None:
        focused = self.focused
        if not (focused and isinstance(focused.parent, ListView) and focused.parent.id == "branches-panel"):
            self.notify("Please select a branch to delete", severity="warning")
            return
        
        if hasattr(focused, 'children') and focused.children:
            child = focused.children[0]
            if isinstance(child, BranchItem):
                branch_name = child.branch_info['name']
                if child.branch_info['is_current']:
                    self.notify("Cannot delete current branch", severity="error")
                    return
                
                if child.branch_info.get('is_remote', False):
                    self.notify("Cannot delete remote branch from here", severity="error")
                    return
                
                confirm = await self.push_screen(ConfirmDialog(
                    "Delete Branch",
                    f"Delete branch '{branch_name}'?"
                ))
                
                if confirm:
                    try:
                        self.git_ops.delete_branch(branch_name)
                        self.notify(f"Deleted branch: {branch_name}")
                        self.refresh_branches()
                    except Exception as e:
                        if "not fully merged" in str(e):
                            force_confirm = await self.push_screen(ConfirmDialog(
                                "Force Delete Branch",
                                f"Branch '{branch_name}' is not fully merged. Force delete?"
                            ))
                            if force_confirm:
                                try:
                                    self.git_ops.delete_branch(branch_name, force=True)
                                    self.notify(f"Force deleted branch: {branch_name}")
                                    self.refresh_branches()
                                except Exception as e2:
                                    self.notify(f"Failed to delete branch: {str(e2)}", severity="error")
                        else:
                            self.notify(f"Failed to delete branch: {str(e)}", severity="error")
    
    async def action_stash(self) -> None:
        status = self.git_ops.get_status()
        if not (status['staged'] or status['unstaged']):
            self.notify("No changes to stash", severity="warning")
            return
        
        message = await self.push_screen(StashDialog())
        if message is not None:
            try:
                self.git_ops.stash(message if message else None)
                self.notify("Changes stashed")
                self.refresh_all()
            except Exception as e:
                self.notify(f"Failed to stash: {str(e)}", severity="error")
    
    def action_stash_pop(self) -> None:
        try:
            stashes = self.git_ops.get_stashes()
            if not stashes:
                self.notify("No stashes to pop", severity="warning")
                return
            
            self.git_ops.stash_pop()
            self.notify("Popped latest stash")
            self.refresh_all()
        except Exception as e:
            self.notify(f"Failed to pop stash: {str(e)}", severity="error")
    
    async def action_merge(self) -> None:
        focused = self.focused
        if not (focused and isinstance(focused.parent, ListView) and focused.parent.id == "branches-panel"):
            self.notify("Please select a branch to merge", severity="warning")
            return
        
        if hasattr(focused, 'children') and focused.children:
            child = focused.children[0]
            if isinstance(child, BranchItem):
                branch_name = child.branch_info['name']
                if child.branch_info['is_current']:
                    self.notify("Cannot merge current branch into itself", severity="error")
                    return
                
                confirm = await self.push_screen(ConfirmDialog(
                    "Merge Branch",
                    f"Merge '{branch_name}' into current branch?"
                ))
                
                if confirm:
                    try:
                        self.git_ops.merge(branch_name)
                        self.notify(f"Merged {branch_name}")
                        self.refresh_all()
                    except Exception as e:
                        self.notify(f"Merge failed: {str(e)}", severity="error")
    
    async def action_rebase(self) -> None:
        focused = self.focused
        if not (focused and isinstance(focused.parent, ListView) and focused.parent.id == "branches-panel"):
            self.notify("Please select a branch to rebase onto", severity="warning")
            return
        
        if hasattr(focused, 'children') and focused.children:
            child = focused.children[0]
            if isinstance(child, BranchItem):
                branch_name = child.branch_info['name']
                if child.branch_info['is_current']:
                    self.notify("Cannot rebase onto current branch", severity="error")
                    return
                
                confirm = await self.push_screen(ConfirmDialog(
                    "Rebase",
                    f"Rebase current branch onto '{branch_name}'?"
                ))
                
                if confirm:
                    try:
                        self.git_ops.rebase(branch_name)
                        self.notify(f"Rebased onto {branch_name}")
                        self.refresh_all()
                    except Exception as e:
                        self.notify(f"Rebase failed: {str(e)}", severity="error")
    
    async def action_diff(self) -> None:
        focused = self.focused
        if focused and isinstance(focused.parent, ListView) and focused.parent.id == "files-panel":
            if hasattr(focused, 'children') and focused.children:
                child = focused.children[0]
                if isinstance(child, FileStatus):
                    file_path = child.file_info['path']
                    status = self.git_ops.get_status()
                    
                    staged = any(f['path'] == file_path for f in status['staged'])
                    diff = self.git_ops.get_diff(file_path, staged=staged)
                    
                    if diff:
                        await self.push_screen(DiffViewer(diff, f"Diff: {file_path}"))
                    else:
                        self.notify("No differences found", severity="info")
    
    async def action_show_commit(self) -> None:
        focused = self.focused
        if focused and isinstance(focused.parent, ListView) and focused.parent.id == "commits-panel":
            if hasattr(focused, 'children') and focused.children:
                child = focused.children[0]
                if isinstance(child, CommitItem):
                    commit_sha = child.commit_info['sha']
                    try:
                        diff = self.git_ops.repo.git.show(commit_sha)
                        await self.push_screen(DiffViewer(
                            diff,
                            f"Commit: {commit_sha} - {child.commit_info['message']}"
                        ))
                    except Exception as e:
                        self.notify(f"Failed to show commit: {str(e)}", severity="error")
    
    def action_help(self) -> None:
        help_text = """
Keyboard Shortcuts:

Navigation:
  Tab        - Next panel
  Shift+Tab  - Previous panel
  ↑/↓        - Navigate items
  q          - Quit

Files:
  s          - Stage/Unstage file
  a          - Stage all files
  u          - Unstage all files
  D          - View diff of selected file

Commits:
  c          - Create commit
  Enter      - Show commit details

Branches:
  b          - Checkout branch
  n          - Create new branch
  d          - Delete branch
  m          - Merge selected branch
  R          - Rebase onto selected branch

Remote:
  p          - Push
  P          - Pull
  f          - Fetch

Stash:
  S          - Stash changes
  Ctrl+S     - Pop latest stash

Other:
  r          - Refresh
  ?          - Show this help
"""
        self.notify(help_text, severity="information", timeout=10)
    
    def _setup_custom_bindings(self):
        keybindings = self.config.get('keybindings', {})
        for action, key in keybindings.items():
            if hasattr(self, f'action_{action}'):
                for i, binding in enumerate(self.BINDINGS):
                    if binding.action == action:
                        self.BINDINGS[i] = Binding(key, action, binding.description)
                        break


def run():
    app = LazyGitApp()
    app.run()