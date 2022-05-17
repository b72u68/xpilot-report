from collections import defaultdict
import csv
from dotenv import load_dotenv
from matplotlib import pyplot as plt
import os
import pathlib
from discord import File, Webhook, RequestsWebhookAdapter
import requests

# load information from .env file
load_dotenv()
RESULTS_FILE = os.getenv('RESULTS_FILE')
GRAPH_NAME = os.getenv('GRAPH_NAME')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

# if file does not exist
if not os.path.isfile(RESULTS_FILE):
    print(f"Error: cannot find {RESULTS_FILE}.")
    exit(1)

# create discord webhook
webhook = Webhook.from_url(WEBHOOK_URL, adapter=RequestsWebhookAdapter())


# draw graph from results file
def visualize(filename):
    results = defaultdict(list)

    with open(filename, 'r', newline='') as results_file:
        results_reader = csv.reader(results_file, delimiter=',')
        next(results_reader)
        for row in results_reader:
            gen = int(row[0])
            _ = int(row[1])
            _ = row[2]
            score = float(row[3])
            results[gen].append(score)
        results_file.close()

    for x, y in results.items():
        plt.scatter([x] * len(y), tuple(y))

    plt.xticks(list(results.keys()))
    plt.xlabel('Gen')
    plt.ylabel('Fitness')
    plt.title('Xpilot-AI GA performance')
    plt.savefig(GRAPH_NAME)


# send report
def send_report(filename):
    results = defaultdict(list)
    message = '''
    Gen, PopulationId, Fitness\n
    '''

    with open(filename, 'r', newline='') as results_file:
        results_reader = csv.reader(results_file, delimiter=',')
        next(results_reader)
        for row in results_reader:
            gen = int(row[0])
            id = int(row[1])
            _ = row[2]
            score = float(row[3])
            results[gen].append((id, score))
            message += f'{gen}, {id}, {score}\n'
        results_file.close()

    webhook.send(message)


# send result graph
def send_graph():
    with open(GRAPH_NAME, 'rb') as graph_file:
        image = File(graph_file)
        graph_file.close()

    webhook.send('', file=image)


if __name__ == "__main__":
    last_access_time = pathlib.Path(RESULTS_FILE).stat().st_mtime

    while True:
        recent_access_time = pathlib.Path(RESULTS_FILE).stat().st_mtime
        if recent_access_time == last_access_time:
            continue

        visualize(RESULTS_FILE)
        send_graph()
