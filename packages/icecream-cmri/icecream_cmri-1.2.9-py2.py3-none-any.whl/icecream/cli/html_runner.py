import argparse
import os
from datetime import datetime
from icecream.core.html_runner import Html_Runner


def main():
    parser = argparse.ArgumentParser(description="执行云测平台离线测试报告")
    parser.add_argument("--plan_dir", required=True, help="计划目录路径")
    parser.add_argument("--plan_name", required=False, help="计划名称")
    parser.add_argument("--env_name", required=False, help="环境名称")

    args = parser.parse_args()
    if not args.plan_name:
        report_dir = os.path.join(os.getcwd(), 'report', datetime.now().strftime('%Y%m%d%H%M%S'))
        plan_names = os.listdir(args.plan_dir)
        for plan_name in plan_names:
            html_runner = Html_Runner(os.path.join(args.plan_dir, plan_name), report_dir=report_dir, env_name=args.env_name)
            html_runner.run()
            html_runner.generat_report()
    else:
        html_runner = Html_Runner(os.path.join(args.plan_dir, plan_name))
        html_runner.run()
        html_runner.generat_report()


if __name__ == '__main__':
    main()
