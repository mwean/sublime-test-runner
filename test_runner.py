import sublime
import sublime_plugin
import os, errno
import subprocess
import re

class RunTests(sublime_plugin.TextCommand):
  def run(self, edit, scope):
    last_run = sublime.load_settings("TestRunner.last-run")

    if scope == "last":
      self.run_test(last_run.get("root_path"), last_run.get("path"), last_run.get("spec_type"))
    else:
      path = self.find_path(scope)

      if re.search("\.exs", path):
        root_path = path
        spec_type = 'elixir'
      elif re.search("\/spec\/", path):
        root_path = re.sub("\/spec\/.*", "", path)
        path = re.sub(".*\/spec\/", "spec/", path)
        spec_type = 'rspec'
      else:
        root_path = re.sub("\/features\/.*", "", path)
        path = re.sub(".*\/features", "features", path)
        spec_type = 'cucumber'

      self.run_test(root_path, path, spec_type)

      last_run.set("spec_type", spec_type)
      last_run.set("path", path)
      last_run.set("root_path", root_path)
      sublime.save_settings("TestRunner.last-run")

  def find_path(self, scope):
    path = self.view.file_name()

    if re.search("(spec)|(features)", path) == None:
      twin_path = get_twin_path(path)
      if os.path.exists(twin_path):
        path = twin_path
      else:
        return sublime.error_message("You're not in a spec, bro.")

    if scope == "line":
      line_number, column = self.view.rowcol(self.view.sel()[0].begin())
      line_number += 1
      path += ":" + str(line_number)

    return path

  def run_test(self, root_path, path, spec_type):
    self.run_in_terminal(root_path, path, spec_type)

  def run_in_terminal(self, root_path, path, spec_type):
    # cd_command = '(SKIP_LS=1 cd "' + root_path + '" && '
    osascript_command = 'osascript '
    osascript_command += '"' + sublime.packages_path() + '/TestRunner/run_command.scpt" "'

    if spec_type == 'rspec':
      osascript_command += 'notify_result spring_spec --fail-fast ' + path + '"'
    elif spec_type == 'elixir':
      osascript_command += 'mix espec ' + path + '"'
    else:
      osascript_command += 'notify_result bundle exec cucumber --color ' + path + '"'

    osascript_command += ' "Spec Runner"'
    os.system(osascript_command)
