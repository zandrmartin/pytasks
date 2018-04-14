_tasks=$(~/src/pytasks/venv/bin/python ~/src/pytasks/completion.py dmenu)
_opts=('-i' '-l' '5' '-fn' 'Noto Sans UI Regular:pixelsize=14' '-p' 'Complete task:')
_task=$(printf '%s\n' "${_tasks[@]}" | dmenu "${_opts[@]}" | cut -d" " -f1 | tr -d "[]")
if [[ $? == 0 ]]; then
    task complete $_task
fi
