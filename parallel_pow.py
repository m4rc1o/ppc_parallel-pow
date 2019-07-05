import sys
import hashlib
from mpi4py import MPI

bloco = {
    'tansacoes': [
                    'marcio->tarik:1000 BTC', 
                    'tarik->breno:50 BTC',
                    'felipe->marcio:10 BTC',
                    'marcio->tarik:10 BTC',
                    'marcio->marcio:20 BTC',
                 ],
    'id': 1256,
    'nounce': 0
}

tempo_ini = MPI.Wtime()

comm = MPI.COMM_WORLD
meu_id = comm.Get_rank()
qtd_processos = comm.Get_size()

bloco['id'] = sys.argv[1] #Para produzir hashs aleatórios de blocos com ids passados via bash
qtd_zeros = int(sys.argv[2])
qtd_testar_total = int(sys.argv[3])

qtd_testar_local = qtd_testar_total // qtd_processos # A faixa de nounces que será testada por cada processo
nounce_ini = meu_id*qtd_testar_local # O nounce inicial da faixa
nounce_fin = (meu_id + 1)*qtd_testar_local # O nounce final da faixa

print("Sou o processo", meu_id, "e vou testar de", nounce_ini, "até", nounce_fin)

bloco_hash = hashlib.sha256((str(bloco)).encode()).hexdigest()
if meu_id == 0:
    print("Hash inicial", bloco_hash)

#Executando os testes nas respectivas faixas
nounce = nounce_ini
encontrado = False
id_quem_achou = -1
contador = 0
while nounce < nounce_fin and not encontrado:
    bloco['nounce'] = nounce
    bloco_hash = hashlib.sha256((str(bloco)).encode()).hexdigest()
    nounce += 1
    
    contador += 1
    
    #Fazendo o iprobe apenas a cada 1000 iterações, pois ele é demorado
    if contador == 1000:
        encontrado = comm.iprobe(source=MPI.ANY_SOURCE, tag=0)
        contador = 0
    
    if bloco_hash[0:qtd_zeros] == '0'*qtd_zeros:
        encontrado = True
        id_quem_achou = meu_id
    
    #Se o processo finalizou, sem sucesso, os testes na sua faixa de nounces
    #ele inicia testes em uma nova faixa
    if nounce == nounce_fin:
        nounce_ini = nounce_ini + qtd_testar_total
        nounce = nounce_ini
        nounce_fin = nounce_ini + qtd_testar_local
        #print("\nSou o processo", meu_id, "e não encontrei nada na faixa anterior")
        #print("agora vou verificar de", nounce, "até", nounce_fin)        

if encontrado and meu_id == id_quem_achou:
    print("O processo", meu_id, "encontrou a prova de trabalho")
    print("Prova de trabalho", bloco['nounce'])
    
    tempo_fim = MPI.Wtime()
    
    #Informando aos outros processos que o hash foi encontrado
    for i in range(qtd_processos):
        comm.isend(encontrado, dest=i, tag=0)
    
#Sincronizando para que o tempo possa sempre ser colocado na última
#posição da lista que será utilizada no colab notebook que executará
#este código
comm.Barrier()
if meu_id == id_quem_achou:
    print("Tempo de execução:", tempo_fim - tempo_ini)
    
    
