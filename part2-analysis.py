# analise_produtor_consumidor.py
import matplotlib.pyplot as plt
import numpy as np
import os
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
BASE_OUTPUT_DIR = PROJECT_ROOT / 'analysis' / 'part2'
DATA_DIR = BASE_OUTPUT_DIR / 'data'
PLOTS_DIR = BASE_OUTPUT_DIR / 'plots'
TIMES_FILE = DATA_DIR / 'execution_times.csv'


def ensure_output_directories():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def collect_occupancy_files():
    files = sorted(DATA_DIR.glob('occupancy_*.txt'))
    if files:
        return files
    return sorted(Path('.').glob('occupancy_*.txt'))


def parse_occupancy_filename(filename):
    name = Path(filename).stem
    parts = name.replace('occupancy_', '').split('_')
    N = int(parts[0][1:])
    P = int(parts[1][1:])
    C = int(parts[2][1:])
    return N, P, C


def plot_output_path(filename):
    ensure_output_directories()
    return PLOTS_DIR / filename

def parse_occupancy_file(filename):
    """Lê arquivo de ocupação e retorna lista de ocupações"""
    occupancies = []
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            for line in f:
                try:
                    occupancies.append(int(line.strip()))
                except:
                    pass
    return occupancies

def parse_execution_times(filename=TIMES_FILE):
    """Lê arquivo CSV com tempos médios e retorna dicionário por N e configuração."""
    results = defaultdict(dict)

    if not Path(filename).exists():
        legacy_file = PROJECT_ROOT / 'execution_times.csv'
        if legacy_file.exists():
            filename = legacy_file
        else:
            print(f"Arquivo {filename} não encontrado. Execute o programa C (part2) primeiro.")
            return results

    with open(filename, 'r') as f:
        next(f, None)  # Ignorar cabeçalho
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(',')
            if len(parts) != 4:
                continue
            try:
                N = int(parts[0])
                P = int(parts[1])
                C = int(parts[2])
                avg_time = float(parts[3])
                results[N][(P, C)] = avg_time
            except ValueError:
                continue

    return results

def plot_execution_times():
    """Gera gráfico de tempo de execução vs configuração de threads"""
    results = parse_execution_times()
    if not results:
        return

    ensure_output_directories()

    # Configurações (Prod, Cons) na ordem desejada para o eixo X
    configs = [(1,1), (1,2), (1,4), (1,8), (2,1), (4,1), (8,1)]
    config_labels = ['P1C1', 'P1C2', 'P1C4', 'P1C8', 'P2C1', 'P4C1', 'P8C1']

    # Criar gráfico
    plt.figure(figsize=(12, 7))

    x = np.arange(len(config_labels))
    n_values = sorted(results.keys())
    width = 0.8 / max(len(n_values), 1)

    colors = ['blue', 'green', 'red', 'orange', 'purple', 'brown', 'cyan']

    for i, N in enumerate(n_values):
        times = [results[N].get(cfg, np.nan) for cfg in configs]
        offset = (i - (len(n_values) - 1) / 2) * width
        plt.bar(
            x + offset,
            times,
            width,
            label=f'N={N}',
            color=colors[i % len(colors)],
            alpha=0.7
        )
    
    plt.xlabel('Configuração (Produtores x Consumidores)')
    plt.ylabel('Tempo Médio de Execução (segundos)')
    plt.title('Tempo de Execução vs Configuração de Threads\n(Produtor-Consumidor com Semáforos)')
    plt.xticks(x, config_labels)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_file = plot_output_path('execution_times.png')
    plt.savefig(output_file, dpi=150)
    print(f"Gráfico salvo em: {output_file}")
    plt.show()

def plot_buffer_occupancy():
    """Gera gráficos de ocupação do buffer para cada configuração"""
    # Procurar arquivos de ocupação
    occupancy_files = collect_occupancy_files()
    
    if not occupancy_files:
        print(f"Nenhum arquivo de ocupação encontrado em {DATA_DIR}. Execute o programa C primeiro.")
        return
    
    # Organizar por N
    files_by_N = defaultdict(list)
    for f in occupancy_files:
        N, _, _ = parse_occupancy_filename(f)
        files_by_N[N].append(f)
    
    # Para cada N, criar um gráfico com todas as configurações
    for N, files in sorted(files_by_N.items()):
        plt.figure(figsize=(14, 8))

        # Ordenar por P e depois por C para manter a legenda consistente.
        ordered_files = sorted(
            files,
            key=lambda name: (
                parse_occupancy_filename(name)[1],
                parse_occupancy_filename(name)[2]
            )
        )

        for f in ordered_files:
            # Extrair configuração
            _, P, C = parse_occupancy_filename(f)
            
            occupancies = parse_occupancy_file(f)
            
            if occupancies:
                # Amostrar para gráfico (se muito grande)
                max_points = 2000
                if len(occupancies) > max_points:
                    step = len(occupancies) // max_points
                    sample_x = range(0, len(occupancies), step)
                    sample_y = [occupancies[i] for i in sample_x]
                else:
                    sample_x = range(len(occupancies))
                    sample_y = occupancies
                
                plt.plot(sample_x, sample_y, label=f'P={P}, C={C}', alpha=0.7, linewidth=1.2)
        
        plt.xlabel('Número da Operação (produção/consumo)')
        plt.ylabel('Ocupação do Buffer')
        plt.title(f'Ocupação do Buffer ao Longo do Tempo (N={N})')
        plt.legend(loc='upper right', fontsize=8)
        plt.grid(True, alpha=0.3)
        plt.ylim(-0.5, N + 0.5)
        
        plt.tight_layout()
        plt.savefig(plot_output_path(f'buffer_occupancy_N{N}.png'), dpi=150)
        plt.show()

def plot_buffer_occupancy_improved():
    """Gráficos de ocupação: versão consolidada + individuais por N"""
    occupancy_files = collect_occupancy_files()
    
    if not occupancy_files:
        print("Nenhum arquivo de ocupação encontrado.")
        return
    
    # Organizar por N
    files_by_N = defaultdict(list)
    for f in occupancy_files:
        N, _, _ = parse_occupancy_filename(f)
        files_by_N[N].append(f)
    
    # Cores para diferentes combinações de (P,C)
    configs = [(1,1), (1,2), (1,4), (1,8), (2,1), (4,1), (8,1)]
    colors = plt.cm.tab10(np.linspace(0, 1, len(configs)))
    config_color = {config: colors[i] for i, config in enumerate(configs)}
    
    # ============================================
    # GRÁFICO 1: VERSÃO CONSOLIDADA (Subplots 2x2)
    # ============================================
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()
    
    for idx, (N, files) in enumerate(sorted(files_by_N.items())):
        ax = axes[idx]
        
        # Agrupar arquivos por (P,C)
        for f in files:
            _, P, C = parse_occupancy_filename(f)
            
            occupancies = parse_occupancy_file(f)
            
            if occupancies and len(occupancies) > 0:
                # Amostragem inteligente
                max_points = 2000
                if len(occupancies) > max_points:
                    step = len(occupancies) // max_points
                    x = list(range(0, len(occupancies), step))
                    y = [occupancies[i] for i in x]
                else:
                    x = list(range(len(occupancies)))
                    y = occupancies
                
                # Suavizar com média móvel para melhor visualização
                window = max(1, len(y) // 200)
                if window > 1:
                    y_smooth = np.convolve(y, np.ones(window)/window, mode='valid')
                    x_smooth = x[:len(y_smooth)]
                else:
                    y_smooth = y
                    x_smooth = x
                
                ax.plot(x_smooth, y_smooth, 
                       label=f'P={P}, C={C}', 
                       color=config_color[(P, C)],
                       alpha=0.8, 
                       linewidth=1.5)
        
        ax.set_xlabel('Número da Operação', fontsize=10)
        ax.set_ylabel('Ocupação do Buffer', fontsize=10)
        ax.set_title(f'Buffer Size N = {N}', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_ylim(-0.5, N + 0.5)
        
        # Limitar eixo x para melhor visualização (opcional)
        if occupancies:
            ax.set_xlim(0, min(len(occupancies), 50000))
    
    # Legenda única para toda a figura consolidada
    handles = []
    labels = []
    for (P, C), color in config_color.items():
        handles.append(plt.Line2D([0], [0], color=color, linewidth=2, label=f'P={P}, C={C}'))
        labels.append(f'P={P}, C={C}')
    
    fig.legend(handles, labels, loc='upper right', bbox_to_anchor=(0.98, 0.98), fontsize=9)
    
    plt.suptitle('Ocupação do Buffer por Configuração e Tamanho N\n(Consolidado)', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(plot_output_path('buffer_occupancy_consolidado.png'), dpi=150, bbox_inches='tight')
    plt.show()
    
    # ============================================
    # GRÁFICOS 2-5: VERSÕES INDIVIDUAIS (um por N)
    # ============================================
    for N, files in sorted(files_by_N.items()):
        plt.figure(figsize=(14, 8))
        
        # Ordenar arquivos por P e depois por C para consistência
        ordered_files = sorted(
            files,
            key=lambda name: (
                parse_occupancy_filename(name)[1],
                parse_occupancy_filename(name)[2]
            )
        )
        
        for f in ordered_files:
            # Extrair configuração
            _, P, C = parse_occupancy_filename(f)
            
            occupancies = parse_occupancy_file(f)
            
            if occupancies:
                # Amostragem inteligente
                max_points = 5000
                if len(occupancies) > max_points:
                    step = len(occupancies) // max_points
                    x = range(0, len(occupancies), step)
                    y = [occupancies[i] for i in x]
                else:
                    x = range(len(occupancies))
                    y = occupancies
                
                # Suavizar com média móvel
                window = max(1, len(y) // 500)
                if window > 1:
                    y_smooth = np.convolve(y, np.ones(window)/window, mode='valid')
                    x_smooth = list(x)[:len(y_smooth)]
                else:
                    y_smooth = y
                    x_smooth = x
                
                plt.plot(x_smooth, y_smooth, 
                        label=f'P={P}, C={C}', 
                        alpha=0.7, 
                        linewidth=1.2)
        
        plt.xlabel('Número da Operação (produção/consumo)', fontsize=12)
        plt.ylabel('Ocupação do Buffer', fontsize=12)
        plt.title(f'Ocupação do Buffer ao Longo do Tempo (N = {N})', fontsize=14, fontweight='bold')
        plt.legend(loc='upper right', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.ylim(-0.5, N + 0.5)
        
        # Ajustar limite do eixo X para foco nas operações iniciais (opcional)
        # plt.xlim(0, min(len(occupancies) if occupancies else 0, 20000))
        
        plt.tight_layout()
        plt.savefig(plot_output_path(f'buffer_occupancy_N{N}_individual.png'), dpi=150, bbox_inches='tight')
        plt.show()
    
    print("\n✓ Gráficos gerados:")
    print("  - buffer_occupancy_consolidado.png (todos N em um único gráfico)")
    for N in files_by_N.keys():
        print(f"  - buffer_occupancy_N{N}_individual.png")

def plot_individual_occupancy_only():
    """Versão que gera APENAS os gráficos individuais (como antes)"""
    occupancy_files = collect_occupancy_files()
    
    if not occupancy_files:
        print(f"Nenhum arquivo de ocupação encontrado em {DATA_DIR}. Execute o programa C primeiro.")
        return
    
    # Organizar por N
    files_by_N = defaultdict(list)
    for f in occupancy_files:
        N, _, _ = parse_occupancy_filename(f)
        files_by_N[N].append(f)
    
    # Para cada N, criar um gráfico separado
    for N, files in sorted(files_by_N.items()):
        plt.figure(figsize=(14, 8))
        
        # Ordenar por P e depois por C para manter a legenda consistente
        ordered_files = sorted(
            files,
            key=lambda name: (
                parse_occupancy_filename(name)[1],
                parse_occupancy_filename(name)[2]
            )
        )
        
        for f in ordered_files:
            # Extrair configuração
            _, P, C = parse_occupancy_filename(f)
            
            occupancies = parse_occupancy_file(f)
            
            if occupancies:
                # Amostragem inteligente:
                # Se for muito grande, usa amostragem proporcional
                if len(occupancies) > 5000:
                    step = len(occupancies) // 5000
                    sample_x = range(0, len(occupancies), step)
                    sample_y = [occupancies[i] for i in sample_x]
                else:
                    sample_x = range(len(occupancies))
                    sample_y = occupancies
                
                # Aplicar suavização para reduzir ruído
                if len(sample_y) > 200:
                    from scipy import signal
                    window = signal.hann(min(51, len(sample_y) // 10))
                    sample_y = signal.convolve(sample_y, window, mode='same') / sum(window)
                
                plt.plot(sample_x, sample_y, label=f'P={P}, C={C}', alpha=0.7, linewidth=0.8)
        
        plt.xlabel('Número da Operação (produção/consumo)')
        plt.ylabel('Ocupação do Buffer')
        plt.title(f'Ocupação do Buffer ao Longo do Tempo (N={N})')
        plt.legend(loc='upper right', fontsize=8)
        plt.grid(True, alpha=0.3)
        plt.ylim(-0.5, N + 0.5)
        
        plt.tight_layout()
        plt.savefig(plot_output_path(f'buffer_occupancy_N{N}.png'), dpi=150)
        plt.show()

def plot_occupancy_heatmap():
    """Gera heatmap de ocupação do buffer"""
    occupancy_files = collect_occupancy_files()
    
    if not occupancy_files:
        return
    
    # Criar subplots para cada configuração significativa
    fig, axes = plt.subplots(2, 4, figsize=(16, 10))
    axes = axes.flatten()
    
    for idx, f in enumerate(occupancy_files[:8]):  # Limitar a 8 gráficos
        N, P, C = parse_occupancy_filename(f)
        
        occupancies = parse_occupancy_file(f)
        
        if occupancies and len(occupancies) > 0:
            # Criar matriz para heatmap (janelas de 100 operações)
            window_size = min(100, len(occupancies) // 50)
            if window_size > 0:
                num_windows = len(occupancies) // window_size
                heatmap_data = []
                for w in range(num_windows):
                    start = w * window_size
                    end = min(start + window_size, len(occupancies))
                    window_avg = sum(occupancies[start:end]) / (end - start)
                    heatmap_data.append(window_avg)
                
                axes[idx].imshow([heatmap_data], aspect='auto', cmap='YlOrRd', 
                                extent=[0, len(heatmap_data), 0, 1])
                axes[idx].set_title(f'N={N}, P={P}, C={C}')
                axes[idx].set_xlabel('Janela de Operações')
                axes[idx].set_ylabel('Ocupação Média')
    
    plt.suptitle('Heatmap da Ocupação do Buffer por Janela de Operações')
    plt.tight_layout()
    plt.savefig(plot_output_path('occupancy_heatmap.png'), dpi=150)
    plt.show()

def plot_buffer_occupancy_improved_2():
    """Gráficos de ocupação preservando oscilações naturais do buffer"""
    occupancy_files = collect_occupancy_files()
    
    if not occupancy_files:
        print("Nenhum arquivo de ocupação encontrado.")
        return
    
    # Organizar por N
    files_by_N = defaultdict(list)
    for f in occupancy_files:
        N, P, C = parse_occupancy_filename(f)
        files_by_N[N].append(f)
    
    # Cores para diferentes combinações de (P,C)
    configs = [(1,1), (1,2), (1,4), (1,8), (2,1), (4,1), (8,1)]
    colors = plt.cm.tab10(np.linspace(0, 1, len(configs)))
    config_color = {config: colors[i] for i, config in enumerate(configs)}
    
    # ============================================
    # GRÁFICO CONSOLIDADO (Subplots 2x2)
    # ============================================
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()
    
    for idx, (N, files) in enumerate(sorted(files_by_N.items())):
        ax = axes[idx]
        
        for f in files:
            _, P, C = parse_occupancy_filename(f)
            
            occupancies = parse_occupancy_file(f)
            
            if occupancies and len(occupancies) > 0:
                # Estratégia de plotagem baseada no tamanho do buffer
                if N <= 10:  # Buffers pequenos: mostrar pontos discretos
                    # Para N=1, mostrar apenas os primeiros pontos para não sobrecarregar
                    max_points = min(len(occupancies), 500)
                    x = list(range(max_points))
                    y = occupancies[:max_points]
                    
                    # Usar scatter para mostrar natureza discreta
                    ax.scatter(x, y, s=1, alpha=0.5, 
                              label=f'P={P}, C={C}',
                              color=config_color[(P, C)])
                    
                    # Opcional: linha de média móvel muito curta para tendência
                    if len(y) > 50:
                        window = 10
                        y_smooth = np.convolve(y, np.ones(window)/window, mode='valid')
                        x_smooth = x[:len(y_smooth)]
                        ax.plot(x_smooth, y_smooth, 
                               color=config_color[(P, C)],
                               alpha=0.3, linewidth=0.5)
                
                elif N <= 100:  # Buffers médios: amostragem moderada
                    max_points = 2000
                    if len(occupancies) > max_points:
                        step = len(occupancies) // max_points
                        x = list(range(0, len(occupancies), step))
                        y = [occupancies[i] for i in x]
                    else:
                        x = list(range(len(occupancies)))
                        y = occupancies
                    
                    # Pequena suavização apenas para reduzir ruído excessivo
                    if len(y) > 200:
                        window = 5
                        y_smooth = np.convolve(y, np.ones(window)/window, mode='valid')
                        x_smooth = x[:len(y_smooth)]
                    else:
                        y_smooth = y
                        x_smooth = x
                    
                    ax.plot(x_smooth, y_smooth, 
                           label=f'P={P}, C={C}', 
                           color=config_color[(P, C)],
                           alpha=0.7, 
                           linewidth=1.0)
                
                else:  # Buffers grandes: plotagem normal com amostragem
                    max_points = 3000
                    if len(occupancies) > max_points:
                        step = len(occupancies) // max_points
                        x = list(range(0, len(occupancies), step))
                        y = [occupancies[i] for i in x]
                    else:
                        x = list(range(len(occupancies)))
                        y = occupancies
                    
                    # Suavização leve
                    if len(y) > 300:
                        window = 20
                        y_smooth = np.convolve(y, np.ones(window)/window, mode='valid')
                        x_smooth = x[:len(y_smooth)]
                    else:
                        y_smooth = y
                        x_smooth = x
                    
                    ax.plot(x_smooth, y_smooth, 
                           label=f'P={P}, C={C}', 
                           color=config_color[(P, C)],
                           alpha=0.7, 
                           linewidth=1.2)
        
        ax.set_xlabel('Número da Operação', fontsize=10)
        ax.set_ylabel('Ocupação do Buffer', fontsize=10)
        ax.set_title(f'Buffer Size N = {N}', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_ylim(-0.5, N + 0.5)
        
        # Ajustar visualização para N=1
        if N == 1:
            ax.set_yticks([0, 1])
            ax.set_ylim(-0.2, 1.2)
    
    # Legenda única
    handles = []
    labels = []
    for (P, C), color in config_color.items():
        handles.append(plt.Line2D([0], [0], color=color, linewidth=2, label=f'P={P}, C={C}'))
        labels.append(f'P={P}, C={C}')
    
    fig.legend(handles, labels, loc='upper right', bbox_to_anchor=(0.98, 0.98), fontsize=9)
    
    plt.suptitle('Ocupação do Buffer por Configuração e Tamanho N\n(Consolidado)', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('buffer_occupancy_consolidado_2.png', dpi=150, bbox_inches='tight')
    plt.show()

def plot_detail_by_n_ranges():
    """Gera gráficos detalhados por N com janelas de visualização específicas."""
    occupancy_files = collect_occupancy_files()
    
    if not occupancy_files:
        print("Nenhum arquivo de ocupação encontrado.")
        return
    
    target_ranges = {
        1: [(50, 'buffer_occupancy_detail_N1.png', 'Detalhe da ocupação do buffer (N=1, 0 a 50)')],
        10: [(360, 'buffer_occupancy_detail_N10.png', 'Detalhe da ocupação do buffer (N=10, 0 a 350)')],
        100: [(210, 'buffer_occupancy_detail_N100.png', 'Detalhe da ocupação do buffer (N=100, 0 a 200)')],
        1000: [
            (2300, 'buffer_occupancy_detail_N1000_0_2000.png', 'Detalhe da ocupação do buffer (N=1000, 0 a 2000)'),
            (170, 'buffer_occupancy_detail_N1000_0_200.png', 'Ultra-detalhe da ocupação do buffer (N=1000, 0 a 200)')
        ],
    }

    files_by_N = defaultdict(list)
    for f in occupancy_files:
        N = parse_occupancy_filename(f)[0]
        if N in target_ranges:
            files_by_N[N].append(f)

    if not files_by_N:
        print("Nenhum buffer alvo encontrado.")
        return

    # Usar o mesmo esquema de cores térmicas dos gráficos individuais.
    config_color, _ = get_config_color_scheme()
    ordered_configs = [(1,8), (1,4), (1,2), (1,1), (2,1), (4,1), (8,1)]

    def plot_window(ax, files, N, max_x, title):
        max_y_in_window = None

        for P, C in ordered_configs:
            matching_file = None
            for f in files:
                _, P_file, C_file = parse_occupancy_filename(f)
                if P_file == P and C_file == C:
                    matching_file = f
                    break

            if not matching_file:
                continue

            occupancies = parse_occupancy_file(matching_file)
            if not occupancies:
                continue

            max_display = min(len(occupancies), max_x + 1)
            x = list(range(max_display))
            y = occupancies[:max_display]

            current_max = max(y)
            if max_y_in_window is None:
                max_y_in_window = current_max
            else:
                max_y_in_window = max(max_y_in_window, current_max)

            ax.step(
                x,
                y,
                where='mid',
                label=f'P={P}, C={C}',
                color=config_color[(P, C)],
                alpha=0.8,
                linewidth=1.1,
            )

        ax.set_xlabel('Número da Operação', fontsize=11)
        ax.set_ylabel('Ocupação do Buffer', fontsize=11)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, max_x)

        if max_y_in_window is None:
            max_y_in_window = 1 if N == 1 else N

        ax.set_ylim(-0.5, max_y_in_window + 0.5)

        if N == 1:
            ax.set_yticks([0, 1])

        ax.legend(loc='lower right', fontsize=10)

    for N, files in sorted(files_by_N.items()):
        windows = target_ranges[N]
        for max_x, filename, title in windows:
            fig, ax = plt.subplots(1, 1, figsize=(6, 6))
            plot_window(ax, files, N, max_x, title)
            fig.suptitle(
                f'Detalhamento da Ocupação do Buffer - N={N}',
                fontsize=14,
                fontweight='bold',
            )
            fig.tight_layout(rect=[0, 0.02, 1, 0.92])
            output_file = plot_output_path(filename)
            fig.savefig(output_file, dpi=150, bbox_inches='tight')
            print(f"Gráfico salvo em: {output_file}")
            plt.show()
            plt.close(fig)

def plot_occupancy_heatmap_2d_by_N():
    """Heatmap 2D mostrando ocupação ao longo do tempo para diferentes (P,C)"""
    occupancy_files = collect_occupancy_files()
    
    if not occupancy_files:
        print("Nenhum arquivo de ocupação encontrado.")
        return
    
    files_by_N = defaultdict(list)
    for f in occupancy_files:
        N = parse_occupancy_filename(f)[0]
        files_by_N[N].append(f)
    
    # Criar um heatmap para cada N
    configs = [(1,8), (1,4), (1,2), (1,1), (2,1), (4,1), (8,1)]
    
    for N, files in sorted(files_by_N.items()):
        # Criar matriz para heatmap
        # Linhas = configurações (P,C), Colunas = janelas de tempo
        heatmap_data = []
        config_labels = []
        
        # Determinar número máximo de janelas
        max_windows = 0
        occupancy_dict = {}
        
        for (P, C) in configs:
            # Encontrar arquivo para esta configuração
            matching_file = None
            for f in files:
                N_file, P_file, C_file = parse_occupancy_filename(f)
                if P_file == P and C_file == C:
                    matching_file = f
                    break
            
            if matching_file:
                occupancies = parse_occupancy_file(matching_file)
                if occupancies:
                    occupancy_dict[(P, C)] = occupancies
                    # Dividir em 50 janelas de tempo
                    num_windows = 50
                    window_size = len(occupancies) // num_windows
                    if window_size > 0:
                        windows = []
                        for w in range(num_windows):
                            start = w * window_size
                            end = start + window_size if w < num_windows - 1 else len(occupancies)
                            window_avg = np.mean(occupancies[start:end])
                            windows.append(window_avg)
                        heatmap_data.append(windows)
                        max_windows = max(max_windows, len(windows))
                        config_labels.append(f'P={P}, C={C}')
        
        if heatmap_data:
            # Padronizar tamanho das linhas
            for i in range(len(heatmap_data)):
                if len(heatmap_data[i]) < max_windows:
                    heatmap_data[i].extend([heatmap_data[i][-1]] * (max_windows - len(heatmap_data[i])))
            
            # Criar heatmap
            fig, ax = plt.subplots(figsize=(14, 8))
            im = ax.imshow(heatmap_data, aspect='auto', cmap='YlOrRd', interpolation='bilinear')
            
            ax.set_yticks(range(len(config_labels)))
            ax.set_yticklabels(config_labels)
            ax.set_xlabel('Janela de Tempo (progressão da execução)', fontsize=11)
            ax.set_ylabel('Configuração (Produtores x Consumidores)', fontsize=11)
            ax.set_title(f'Ocupação do Buffer ao Longo do Tempo - N = {N}', fontsize=13, fontweight='bold')
            
            # Colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('Ocupação Média do Buffer', fontsize=10)
            
            plt.tight_layout()
            plt.savefig(f'occupancy_heatmap_N{N}.png', dpi=150, bbox_inches='tight')
            plt.show()

def generate_statistics():
    """Gera estatísticas dos resultados"""
    occupancy_files = collect_occupancy_files()
    
    print("\n" + "="*70)
    print("ESTATÍSTICAS DE OCUPAÇÃO DO BUFFER")
    print("="*70)
    
    for f in occupancy_files:
        N, P, C = parse_occupancy_filename(f)
        
        occupancies = parse_occupancy_file(f)
        
        if occupancies:
            avg_occupancy = np.mean(occupancies)
            max_occupancy = np.max(occupancies)
            min_occupancy = np.min(occupancies)
            std_occupancy = np.std(occupancies)
            
            print(f"\nConfiguração: N={N}, P={P}, C={C}")
            print(f"  Ocupação média: {avg_occupancy:.2f}")
            print(f"  Ocupação máxima: {max_occupancy}")
            print(f"  Ocupação mínima: {min_occupancy}")
            print(f"  Desvio padrão: {std_occupancy:.2f}")



import matplotlib.pyplot as plt
import numpy as np
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from matplotlib import patheffects as pe
from collections import defaultdict

def get_config_color(P, C, colormap='coolwarm'):
    """
    Retorna cor baseada na razão Produtor/Consumidor.
    Cores quentes: mais consumidores (P/C < 1)
    Cores neutras: equilibrado (P/C = 1)
    Cores frias: mais produtores (P/C > 1)
    """
    # Calcular razão logarítmica para melhor distribuição
    if P == 0 or C == 0:
        ratio = 0
    else:
        # log2 da razão para simetria: log2(1/8) = -3, log2(1)=0, log2(8)=3
        ratio = np.log2(P / C)
    
    # Normalizar entre -3 e 3 (extremos: 1/8 e 8/1)
    norm_ratio = (ratio + 3) / 6  # Mapeia -3..3 para 0..1
    
    # Usar colormap: quente (vermelho) para ratio < 1, frio (azul) para ratio > 1
    cmap = plt.cm.get_cmap(colormap)
    color = cmap(norm_ratio)
    
    return color, ratio

def get_config_color_scheme():
    """Define o esquema de cores para todas as configurações"""
    configs = [(1,8), (1,4), (1,2), (1,1), (2,1), (4,1), (8,1)]
    
    config_colors = {}
    config_ratios = {}
    
    for P, C in configs:
        color, ratio = get_config_color(P, C, 'coolwarm')
        config_colors[(P, C)] = color
        config_ratios[(P, C)] = ratio
        
        # Debug: imprimir cores atribuídas
        ratio_desc = f"P/C = {P}/{C} = {P/C:.2f}"
        if P < C:
            dom = f"🔥 Consumidor-dominante (log2={ratio:.2f})"
        elif P > C:
            dom = f"❄️ Produtor-dominante (log2={ratio:.2f})"
        else:
            dom = f"⚖️ Equilibrado (log2={ratio:.2f})"
        
        print(f"  P={P}, C={C}: {dom} -> cor {color[:3]}")
    
    return config_colors, config_ratios

def plot_buffer_occupancy_with_thermal_colors():
    """
    Gráficos de ocupação com cores térmicas representando
    o balanço entre produtores e consumidores
    """
    occupancy_files = collect_occupancy_files()
    
    if not occupancy_files:
        print("Nenhum arquivo de ocupação encontrado.")
        return
    
    # Organizar por N
    files_by_N = defaultdict(list)
    for f in occupancy_files:
        N = parse_occupancy_filename(f)[0]
        files_by_N[N].append(f)
    
    # Obter esquema de cores térmicas
    config_colors, config_ratios = get_config_color_scheme()
    
    # Ordem desejada para legenda (quente -> frio)
    ordered_configs = [(1,8), (1,4), (1,2), (1,1), (2,1), (4,1), (8,1)]
    
    # ============================================
    # GRÁFICO CONSOLIDADO COM SUBPLOTS
    # ============================================
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()
    
    for idx, (N, files) in enumerate(sorted(files_by_N.items())):
        ax = axes[idx]
        
        # Plotar configurações na ordem definida
        for P, C in ordered_configs:
            # Encontrar arquivo para esta configuração
            matching_file = None
            for f in files:
                _, P_, C_ = parse_occupancy_filename(f)
                if P_ == P and C_ == C:
                    matching_file = f
                    break
            
            if matching_file:
                occupancies = parse_occupancy_file(matching_file)
                
                if occupancies and len(occupancies) > 0:
                    color = config_colors[(P, C)]
                    
                    # Estratégia de plotagem baseada no tamanho do buffer
                    if N == 1:
                        # Buffer pequeno: mostrar oscilações
                        max_display = min(len(occupancies), 1000)
                        x = list(range(max_display))
                        y = occupancies[:max_display]
                        ax.step(x, y, where='mid', 
                               label=f'P={P}, C={C}', 
                               color=color,
                               alpha=0.8, 
                               linewidth=1.2)
                    
                    elif N <= 100:
                        # Buffer médio
                        max_points = 2000
                        if len(occupancies) > max_points:
                            step = len(occupancies) // max_points
                            x = list(range(0, len(occupancies), step))
                            y = [occupancies[i] for i in x]
                        else:
                            x = list(range(len(occupancies)))
                            y = occupancies
                        
                        ax.plot(x, y, 
                               label=f'P={P}, C={C}', 
                               color=color,
                               alpha=0.7, 
                               linewidth=1.0)
                    
                    else:
                        # Buffer grande
                        max_points = 3000
                        if len(occupancies) > max_points:
                            step = len(occupancies) // max_points
                            x = list(range(0, len(occupancies), step))
                            y = [occupancies[i] for i in x]
                        else:
                            x = list(range(len(occupancies)))
                            y = occupancies
                        
                        ax.plot(x, y, 
                               label=f'P={P}, C={C}', 
                               color=color,
                               alpha=0.7, 
                               linewidth=1.0)
        
        ax.set_xlabel('Número da Operação', fontsize=10)
        ax.set_ylabel('Ocupação do Buffer', fontsize=10)
        ax.set_title(f'Buffer Size N = {N}', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_ylim(-0.5, N + 0.5)
        
        if N == 1:
            ax.set_yticks([0, 1])
            ax.set_ylim(-0.2, 1.2)
    
    # Criar legenda com gradiente de cores
    legend_elements = []
    for P, C in ordered_configs:
        color = config_colors[(P, C)]
        ratio_desc = f"P/C = {P}/{C}" if P != C else f"P/C = {P}/{C} (neutro)"
        legend_elements.append(plt.Line2D([0], [0], color=color, linewidth=2, 
                                         label=ratio_desc))
    
    fig.legend(handles=legend_elements, loc='upper right', 
               bbox_to_anchor=(0.98, 0.98), fontsize=9)
    
    plt.suptitle('Ocupação do Buffer - Cores Térmicas\n(🔥 Consumidor-dominante | ⚖️ Neutro | ❄️ Produtor-dominante)', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('buffer_occupancy_thermal_consolidado.png', dpi=150, bbox_inches='tight')
    plt.show()


def plot_individual_with_thermal_colors():
    """
    Gráficos individuais por N com cores térmicas
    """
    occupancy_files = collect_occupancy_files()
    
    if not occupancy_files:
        print("Nenhum arquivo de ocupação encontrado.")
        return
    
    files_by_N = defaultdict(list)
    for f in occupancy_files:
        N = parse_occupancy_filename(f)[0]
        files_by_N[N].append(f)
    
    config_colors, _ = get_config_color_scheme()
    ordered_configs = [(1,8), (1,4), (1,2), (1,1), (2,1), (4,1), (8,1)]
    line_styles = ['-', '--', '-.', ':', (0, (5, 1)), (0, (3, 1, 1, 1)), (0, (1, 1))]
    style_by_config = {cfg: line_styles[i] for i, cfg in enumerate(ordered_configs)}
    
    for N, files in sorted(files_by_N.items()):
        fig, ax = plt.subplots(figsize=(14, 8))
        
        for P, C in ordered_configs:
            # Encontrar arquivo
            matching_file = None
            for f in files:
                N_file, P_file, C_file = parse_occupancy_filename(f)
                if P_file == P and C_file == C:
                    matching_file = f
                    break
            
            if matching_file:
                occupancies = parse_occupancy_file(matching_file)
                
                if occupancies:
                    color = config_colors[(P, C)]
                    linestyle = style_by_config[(P, C)]
                    
                    if N == 1:
                        max_display = min(len(occupancies), 1000)
                        x = list(range(max_display))
                        y = occupancies[:max_display]
                        line = ax.step(x, y, where='mid', 
                                       label=f'P={P}, C={C}', 
                                       color=color,
                                       linestyle=linestyle,
                                       alpha=0.85, 
                                       linewidth=1.2,
                                       zorder=3)[0]
                        line.set_path_effects([
                            pe.Stroke(linewidth=2.4, foreground='white', alpha=0.35),
                            pe.Normal()
                        ])
                    
                    else:
                        max_points = 3000 if N > 100 else 2000
                        if len(occupancies) > max_points:
                            step = len(occupancies) // max_points
                            x = list(range(0, len(occupancies), step))
                            y = [occupancies[i] for i in x]
                        else:
                            x = list(range(len(occupancies)))
                            y = occupancies
                        
                        line = ax.plot(x, y, 
                                       label=f'P={P}, C={C}', 
                                       color=color,
                                       linestyle=linestyle,
                                       alpha=0.65, 
                                       linewidth=1.0,
                                       zorder=2)[0]
                        line.set_path_effects([
                            pe.Stroke(linewidth=2.0, foreground='white', alpha=0.28),
                            pe.Normal()
                        ])
        
        ax.set_xlabel('Número da Operação', fontsize=12)
        ax.set_ylabel('Ocupação do Buffer', fontsize=12)
        
        if N == 1:
            ax.set_title(f'Ocupação do Buffer (N={N}) - Cores Térmicas\n🔥 Mais Consumidores | ⚖️ Neutro | ❄️ Mais Produtores', 
                        fontsize=14, fontweight='bold')
            ax.set_yticks([0, 1])
        else:
            ax.set_title(f'Ocupação do Buffer (N={N}) - Cores Térmicas\n🔥 Mais Consumidores | ⚖️ Neutro | ❄️ Mais Produtores', 
                        fontsize=14, fontweight='bold')
        
        ax.legend(loc='center right', fontsize=15, frameon=True)
        ax.set_axisbelow(True)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(-0.5, N + 0.5)
        
        plt.tight_layout()
        plt.savefig(plot_output_path(f'buffer_occupancy_thermal_N{N}.png'), dpi=150, bbox_inches='tight')
        plt.show()




if __name__ == "__main__":
    print("=== ANÁLISE DO PRODUTOR-CONSUMIDOR ===")
    ensure_output_directories()
    
    # Gerar gráficos
    print("\n1. Gerando gráfico de tempos de execução...")
    plot_execution_times()
    
    # print("\n2. Gerando gráficos de ocupação do buffer...")
    # plot_buffer_occupancy()
    
    # plot_buffer_occupancy_improved()
    #plot_buffer_occupancy_improved_2()

    plot_detail_by_n_ranges()

    plot_occupancy_heatmap_2d_by_N()
    
    # print("\n3. Gerando heatmap de ocupação...")
    # plot_occupancy_heatmap()
    
    # print("\n4. Gerando estatísticas...")
    # generate_statistics()


    # print("1. Gerando gráfico consolidado com cores térmicas...")
    # plot_buffer_occupancy_with_thermal_colors()

    # print("\n2. Gerando gráficos individuais com cores térmicas...")
    # plot_individual_with_thermal_colors()

    
    print("\n=== ANÁLISE CONCLUÍDA ===")