#
# This file is the default set of rules to compile a Pebble application.
#
# Feel free to customize this to your needs.
#
import os.path
import os
import sys
from waflib import Context
top = '.'
out = 'build'


def options(ctx):
    # The Pebble SDK tools are in three different locations. We must add all
    # of them to the Python path for the build to work.

    # --- Path 1: The 'extras' directory for pebble_sdk.py itself ---
    base_waf_dir = Context.waf_dir
    extras_dir = os.path.join(base_waf_dir, 'waflib', 'extras')
    sys.path.insert(0, extras_dir)

    # --- Path 2: The 'common/tools' directory for dependencies like generate_appinfo ---
    sdk_dir = os.path.dirname(base_waf_dir)
    common_tools_dir = os.path.join(sdk_dir, 'common', 'tools')
    sys.path.insert(0, common_tools_dir)

    # --- Path 3: The 'common/waftools' directory for the 'resources' package ---
    common_waftools_dir = os.path.join(sdk_dir, 'common', 'waftools')
    sys.path.insert(0, common_waftools_dir)


    # --- Load the Tool ---
    # Now that all three required directories are on the path, load the tool.
    ctx.load('pebble_sdk')



def configure(ctx):
    """
    This method is used to configure your build. ctx.load(`pebble_sdk`) automatically configures
    a build for each valid platform in `targetPlatforms`. Platform-specific configuration: add your
    change after calling ctx.load('pebble_sdk') and make sure to set the correct environment first.
    Universal configuration: add your change prior to calling ctx.load('pebble_sdk').
    """
    ctx.load('pebble_sdk')


def build(ctx):
    ctx.load('pebble_sdk')

    build_worker = os.path.exists('worker_src')
    binaries = []

    cached_env = ctx.env
    for platform in ctx.env.TARGET_PLATFORMS:
        ctx.env = ctx.all_envs[platform]
        ctx.set_group(ctx.env.PLATFORM_NAME)
        app_elf = '{}/pebble-app.elf'.format(ctx.env.BUILD_DIR)
        ctx.pbl_build(source=ctx.path.ant_glob('src/c/**/*.c'), target=app_elf, bin_type='app')

        if build_worker:
            worker_elf = '{}/pebble-worker.elf'.format(ctx.env.BUILD_DIR)
            binaries.append({'platform': platform, 'app_elf': app_elf, 'worker_elf': worker_elf})
            ctx.pbl_build(source=ctx.path.ant_glob('worker_src/c/**/*.c'),
                          target=worker_elf,
                          bin_type='worker')
        else:
            binaries.append({'platform': platform, 'app_elf': app_elf})
    ctx.env = cached_env

    ctx.set_group('bundle')
    ctx.pbl_bundle(binaries=binaries,
                   js=ctx.path.ant_glob(['src/pkjs/**/*.js',
                                         'src/pkjs/**/*.json',
                                         'src/common/**/*.js']),
                   js_entry_file='src/pkjs/index.js')
