project('west-main-project',
        'c',
        version : '0.1',
        default_options : ['warning_level=3'])

exe = executable('west-main-project',
                 sources: ['src/main.c'],
                 name_suffix: 'elf'
                )

test('basic', exe)
