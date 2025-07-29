import csv
import matplotlib.pyplot as plt
from matplotlib import font_manager

font_dirs = "/usr/share/fonts-comic-neue/woff2"
font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
for font_file in font_files:
    font_manager.fontManager.addfont(font_file)

with plt.xkcd():
    requests = plt.figure()
    ax = requests.add_axes((0.1, 0.2, 0.8, 0.7))
    ax.set_xticks([0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000])
    ax.set_yticks([0, 20000, 40000, 60000, 80000, 100000, 120000, 140000, 160000])

    conns = [100, 200, 300, 400, 500, 750, 1000, 2500, 5000, 7500, 10000]
    reqs = {}
    with open('requests.csv') as reqf:
        reqf.readline()  # skip first line
        reqreader = csv.reader(reqf, delimiter=',')
        for row in reqreader:
            reqs[row[0]] = [float(val) for val in row[1:]]

    ax.plot(conns, reqs['Bjoern'], color='#1f77b4', label='Bjoern')
    ax.plot(conns, reqs['Cheroot'], color='#ff7f0e', label='Cheroot')
    ax.plot(conns, reqs['Gunicorn'], color='#2ca02c', label='Gunicorn')
    ax.plot(conns, reqs['Pyruvate'], color='#d62728', label='Pyruvate')
    ax.plot(conns, reqs['Waitress'], color='#9467bd', label='Waitress')
    ax.plot(conns, reqs['uWSGI'], color='#8c564b', label='uWSGI')

    ax.legend()

    ax.set_xlabel('Simultaneous connections')
    ax.set_ylabel('Requests/s')
    requests.text(
        0.5, 0.8,
        'Requests Served',
        ha='center')

    latencies = plt.figure()
    ax = latencies.add_axes((0.1, 0.2, 0.8, 0.7))
    ax.set_xticks([0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000])
    ax.set_yticks([0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000])

    conns = [100, 200, 300, 400, 500, 750, 1000, 2500, 5000, 7500, 10000]
    lats = {}
    with open('latencies.csv') as latf:
        latf.readline()  # skip first line
        latreader = csv.reader(latf, delimiter=',')
        for row in latreader:
            lats[row[0]] = [float(val) for val in row[1:]]

    ax.plot(conns, lats['Bjoern'], color='#1f77b4', label='Bjoern')
    ax.plot(conns, lats['Cheroot'], color='#ff7f0e', label='Cheroot')
    ax.plot(conns, lats['Gunicorn'], color='#2ca02c', label='Gunicorn')
    ax.plot(conns, lats['Pyruvate'], color='#d62728', label='Pyruvate')
    ax.plot(conns, lats['Waitress'], color='#9467bd', label='Waitress')
    ax.plot(conns, lats['uWSGI'], color='#8c564b', label='uWSGI')

    ax.legend()

    ax.set_xlabel('Simultaneous connections')
    ax.set_ylabel('Milliseconds')
    latencies.text(
        0.5, 0.8,
        'Latencies',
        ha='center')

    cpu = plt.figure()
    ax = cpu.add_axes((0.1, 0.2, 0.8, 0.7))
    ax.set_xticks([0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000])
    ax.set_yticks([0, 50, 100, 150, 200, 250, 300, 350, 400, 450])

    conns = [100, 200, 300, 400, 500, 750, 1000, 2500, 5000, 7500, 10000]
    cpus = {}
    with open('cpu.csv') as cpuf:
        cpuf.readline()  # skip first line
        cpureader = csv.reader(cpuf, delimiter=',')
        for row in cpureader:
            cpus[row[0]] = [float(val) for val in row[1:]]

    ax.plot(conns, cpus['Bjoern'], color='#1f77b4', label='Bjoern')
    ax.plot(conns, cpus['Cheroot'], color='#ff7f0e', label='Cheroot')
    ax.plot(conns, cpus['Gunicorn'], color='#2ca02c', label='Gunicorn')
    ax.plot(conns, cpus['Pyruvate'], color='#d62728', label='Pyruvate')
    ax.plot(conns, cpus['Waitress'], color='#9467bd', label='Waitress')
    ax.plot(conns, cpus['uWSGI'], color='#8c564b', label='uWSGI')

    ax.legend()

    ax.set_xlabel('Simultaneous connections')
    ax.set_ylabel('CPU [%]')
    cpu.text(
        0.5, 0.8,
        'CPU Usage',
        ha='center')

    memory = plt.figure()
    ax = memory.add_axes((0.1, 0.2, 0.8, 0.7))
    ax.set_xticks([0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000])
    ax.set_yticks([0, 50, 100, 150, 200, 250, 300, 350, 400, 450])

    conns = [100, 200, 300, 400, 500, 750, 1000, 2500, 5000, 7500, 10000]
    mem = {}
    with open('memory.csv') as memf:
        memf.readline()  # skip first line
        memreader = csv.reader(memf, delimiter=',')
        for row in memreader:
            mem[row[0]] = [float(val) for val in row[1:]]

    ax.plot(conns, mem['Bjoern'], color='#1f77b4', label='Bjoern')
    ax.plot(conns, mem['Cheroot'], color='#ff7f0e', label='Cheroot')
    ax.plot(conns, mem['Gunicorn'], color='#2ca02c', label='Gunicorn')
    ax.plot(conns, mem['Pyruvate'], color='#d62728', label='Pyruvate')
    ax.plot(conns, mem['Waitress'], color='#9467bd', label='Waitress')
    ax.plot(conns, mem['uWSGI'], color='#8c564b', label='uWSGI')

    ax.legend()

    ax.set_xlabel('Simultaneous connections')
    ax.set_ylabel('RAM [MB]')
    memory.text(
        0.5, 0.8,
        'Memory Consumption',
        ha='center')

    errors = plt.figure()
    ax = errors.add_axes((0.1, 0.2, 0.8, 0.7))
    ax.set_xticks([0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000])
    ax.set_yticks([0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000])

    conns = [100, 200, 300, 400, 500, 750, 1000, 2500, 5000, 7500, 10000]
    errs = {}
    with open('errors.csv') as errsf:
        errsf.readline()  # skip first line
        errreader = csv.reader(errsf, delimiter=',')
        for row in errreader:
            errs[row[0]] = [float(val) for val in row[1:]]

    ax.plot(conns, errs['Bjoern'], color='#1f77b4', label='Bjoern')
    ax.plot(conns, errs['Cheroot'], color='#ff7f0e', label='Cheroot')
    ax.plot(conns, errs['Gunicorn'], color='#2ca02c', label='Gunicorn')
    ax.plot(conns, errs['Pyruvate'], color='#d62728', label='Pyruvate')
    ax.plot(conns, errs['Waitress'], color='#9467bd', label='Waitress')
    # ax.plot(conns, errs['uWSGI'], color='#8c564b', label='uWSGI')

    ax.legend()

    ax.set_xlabel('Simultaneous connections')
    ax.set_ylabel('# Socket Errors')
    errors.text(
        0.5, 0.8,
        'Errors (uWSGI hidden)',
        ha='center')

plt.show()
