# Kitchen sink example showcasing a lot of nu syntax,
# taken from various scripts from the main nushell repo: https://github.com/nushell/nushell
# Don't actually run this, please!!!

def animals [] { ["cat", "dog", "eel" ] }
def my-command [animal: string@animals] { print $animal }

export module "🤔🐘" {
  export const foo = "🤔🐘";
}

export use std-rf
export use std-rfc/clip [ copy, paste ]
use std null_d
use 🤔🐘 [ foo, ]

let greeting = "Hello"

echo $gre

str substring 1..
| ansi strip

# User defined one
export def "foo bar" [] {
  # inside a block
  (
    # same line
    "🤔🤖🐘" | str substring 1.. | ansi strip
  )
}

foo bar

overlay use foo
use std/assert

assert equal

overlay use ./foo.nu as prefix --prefix
alias aname = prefix mod name sub module cmd  name  long
aname
prefix foo str
overlay hide prefix

use ./foo.nu [ "mod name" cst_mod ]

$cst_mod."sub module"."sub sub module".var_name
mod name sub module cmd name long
let $cst_mod = 1
$cst_mod

alias "orig update" = update

# Update a column to have a new value if it exists.
#
# If the column exists with the value `null` it will be skipped.
export def "update" [
    field: cell-path # The name of the column to maybe update.
    value: any # The new value to give the cell(s), or a closure to create the value.
]: [record -> record, table -> table, list<any> -> list<any>] {
    let input = $in
    match ($input | describe | str replace --regex '<.*' '') {
        record => {
            if ($input | get -i $field) != null {
                $input | orig update $field $value
            } else { $input }
        }
        table|list => {
            $input | each {|| update $field $value }
        }
        _ => { $input | orig update $field $value }
    }
}

if $nu.os-info.family == 'windows' {
    # fix encoding on Windows https://stackoverflow.com/a/63573649
    load-env {
        PYTHONIOENCODING: utf-8
        PYTHONLEGACYWINDOWSSTDIO: utf-8
    }
}

let env_name = 'e-$ èрт🚒♞中片-j'

let paths = if $nu.os-info.family == 'windows' {
    ['Scripts', 'python.exe']
} else {
    ['bin', 'python']
}

let subdir = $paths.0
let exe = $paths.1

let test_lines = [
    "python -c 'import sys; print(sys.executable)'"                                  # 1
    `python -c 'import os; import sys; v = os.environ.get("VIRTUAL_ENV"); print(v)'` # 2
    $"overlay use '([$env.PWD $env_name $subdir activate.nu] | path join)'"
    "python -c 'import sys; print(sys.executable)'"                                  # 3
    `python -c 'import os; import sys; v = os.environ.get("VIRTUAL_ENV"); print(v)'` # 4
    "print $env.VIRTUAL_ENV_PROMPT"                                                  # 5
    "deactivate"
    "python -c 'import sys; print(sys.executable)'"                                  # 6
    `python -c 'import os; import sys; v = os.environ.get("VIRTUAL_ENV"); print(v)'` # 7
]

def main [] {
    let orig_python_interpreter = (python -c 'import sys; print(sys.executable)')

    let expected = [
        $orig_python_interpreter                           # 1
        "None"                                             # 2
        ([$env.PWD $env_name $subdir $exe] | path join)    # 3
        ([$env.PWD $env_name] | path join)                 # 4
        $env_name                                          # 5
        $orig_python_interpreter                           # 6
        "None"                                             # 7
    ]

    virtualenv $env_name

    $test_lines | save script.nu
    let out = (nu script.nu | lines)

    let o = ($out | str trim | str join (char nl))
    let e = ($expected | str trim | str join (char nl))
    if $o != $e {
        let msg = $"OUTPUT:\n($o)\n\nEXPECTED:\n($e)"
        error make {msg: $"Output does not match the expected value:\n($msg)"}
    }
    rm script.nu
}

use std/log warning

print '-------------------------------------------------------------------'
print 'Building nushell (nu) and all the plugins'
print '-------------------------------------------------------------------'

warning "./scripts/build-all.nu will be deprecated, please use the `toolkit build` command instead"

let repo_root = ($env.CURRENT_FILE | path dirname --num-levels 2)

def build-nushell [] {
    print $'(char nl)Building nushell'
    print '----------------------------'

    cd $repo_root
    cargo build --locked
}

def build-plugin [] {
    let plugin = $in

    print $'(char nl)Building ($plugin)'
    print '----------------------------'

    cd $'($repo_root)/crates/($plugin)'
    cargo build
}

let plugins = [
    nu_plugin_inc,
    nu_plugin_gstat,
    nu_plugin_query,
    nu_plugin_example,
    nu_plugin_custom_values,
    nu_plugin_formats,
    nu_plugin_polars
]

for plugin in $plugins {
    $plugin | build-plugin
}
