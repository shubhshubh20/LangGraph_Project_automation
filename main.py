# Run the graph to see the state at each step
import os
import sys
import threading
from bot.worker import poll_job_status
from bot.telegram_bot import main
from graph.flow import state_worker, safe_replace 
from demo_logger.json_logger import log_event, shutdown_logger
from pathlib import Path

server_name = "http://localhost:8188"
base_dir = Path(__file__).parent
# staging_location = Path("D:\\youtube\\corner_table\\LangGraph_Project_automation\\comfyUI\\staging_loc")
staging_location = base_dir / "comfyUI" / "staging_loc"

if __name__ == "__main__":


    episode_number = sys.argv[1] if len(sys.argv) > 1 else "s01_e08"
    staging_location = staging_location / episode_number

    staging_location.mkdir(parents=True, exist_ok=True)
    

    # check if episodenumber_final_state.json already exists, if yes, ask user if they still want to run the system and overwrite the file
    final_state_file = f"{episode_number}_final_state.json"
    if os.path.exists(final_state_file):
        response = input(f"{final_state_file} already exists. Do you want to overwrite it? (y/n): ")
        if response.lower() != "y":
            print("Exiting without running the system.")
            sys.exit(0)


    
    # state_thread = threading.Thread(target=state_worker, daemon=True)
    # state_thread.start()
    shutdown_event = threading.Event()
    
    telegram_thread = threading.Thread(target=main, args=(episode_number, server_name, staging_location.__str__()), name="TelegramBot", daemon=True)
    telegram_thread.start()
    # main()

    state_worker_thread = threading.Thread(target=state_worker, name="StateWorker", daemon=True)
    state_worker_thread.start()
    # state_worker()

    # Create and start the polling thread
    polling_thread = threading.Thread(target=poll_job_status, args=(server_name, shutdown_event,), name="JobStatusPoller", daemon=True)
    polling_thread.start()


    shutdown_event.wait()

    print("✅ Shutdown signal received. Exiting main thread...")

    print("Joining polling_thread...")
    polling_thread.join(timeout=5)
    print("Polling thread joined (or timeout)")

    print("Joining state_worker_thread...")
    state_worker_thread.join(timeout=5)
    print("State worker thread joined (or timeout)")

    print("Joining telegram_thread...")
    telegram_thread.join(timeout=5)
    print("Telegram thread joined (or timeout)")
    print("✅ System exited cleanly")

    shutdown_logger()
    
    #save the final state to a json file for debugging
    log_event(f'Saving final state to {episode_number}_final_state.json')
    safe_replace('state.json', f'{episode_number}_final_state.json')
    safe_replace('system.log', f'{episode_number}_system.log')



    