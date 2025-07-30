import argparse
from pathlib import Path
from .templates import create_handler_template, create_keyboard_template, create_states_template


def main():
    parser = argparse.ArgumentParser(
        description="Создает шаблоны обработчиков для aiogram"
    )
    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")

    # Команда handler
    handler_parser = subparsers.add_parser("handler", help="Создать шаблоны обработчика")
    handler_parser.add_argument("name", help="Название функции в snake_case")
    handler_parser.add_argument(
        "-d", "--dir",
        default=".",
        help="Целевая директория (по умолчанию: текущая)"
    )

    args = parser.parse_args()

    if args.command == "handler":
        target_dir = Path(args.dir) / "bot" / args.name
        target_dir.mkdir(parents=True, exist_ok=True)

        create_handler_template(args.name, target_dir)
        create_keyboard_template(args.name, target_dir)
        create_states_template(args.name, target_dir)

        print(f"Шаблоны созданы в: {target_dir}")
        print(f"Файлы:")
        print(f"  • {args.name}_handler.py")
        print(f"  • {args.name}_keyboard.py")
        print(f"  • {args.name}_states.py")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()