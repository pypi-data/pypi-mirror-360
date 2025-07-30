import argparse
import threading
from .client import NineBitCIQClient


def on_complete(wf_id, result):
    print(f"[Callback] Workflow {wf_id} completed:")
    print(result)


def async_wait(client, wf_id):
    try:
        result = client.wait_for_completion(wf_id)
        on_complete(wf_id, result)
    except Exception as e:
        print(f"[Callback Error] {e}")


def main():
    parser = argparse.ArgumentParser(description="NineBit CIQ CLI")
    parser.add_argument("--base-url", required=True, help="Base URL of CIQ API")
    parser.add_argument("--api-key", required=True, help="API key for authentication")

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("get-workflow", help="Get design time workflow JSON")

    trigger_parser = subparsers.add_parser("trigger-workflow", help="Trigger a workflow")
    trigger_parser.add_argument("--data", required=True, help="Workflow data JSON string")

    status_parser = subparsers.add_parser("get-status", help="Get workflow status")
    status_parser.add_argument(
        "--async",
        dest="async_mode",
        action="store_true",
        help="Run status check in background",
    )
    status_parser.add_argument("--wf-id", required=True, help="Workflow ID")

    args = parser.parse_args()

    client = NineBitCIQClient(args.base_url, args.api_key)

    if args.command == "get-workflow":
        print(client.get_design_time_workflow())

    elif args.command == "trigger-workflow":
        import json

        data = json.loads(args.data)
        wf_id = client.trigger_workflow(data)
        print(f"Workflow triggered with ID: {wf_id}")

    elif args.command == "get-status":
        if args.async_mode:
            thread = threading.Thread(target=async_wait, args=(client, args.wf_id))
            thread.start()
            print(f"Started non-blocking wait for workflow {args.wf_id}...")
        else:
            result = client.wait_for_completion(args.wf_id)
            print(result)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
