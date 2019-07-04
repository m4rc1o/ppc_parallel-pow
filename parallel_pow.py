import sys
import hashlib
from mpi4py import MPI

bloco = {
    "tansacoes": [
                    "marcio->tarik:1000BTC", 
                    "tarik->breno:500BTC",
                    "felipe->marcio:10BTC",
                    "marcio->tarik:10BTC",
                    "marcio->marcio:0.5BTC",
                 ],
    "id": 1789,
    "nounce": 0
}

tempo_ini = MPI.Wtime()

comm = MPI.COMM_WORLD
meu_id = comm.Get_rank()
qtd_processos = comm.Get_size()

qtd_zeros = int(sys.argv[1])
qtd_testar_total = int(sys.argv[2])

qtd_testar_local = qtd_testar_total // qtd_processos
nounce_ini = meu_id*qtd_testar_local
nounce_fin = (meu_id + 1)*qtd_testar_local

print("Sou o processo", meu_id, "e vou testar de", nounce_ini, "até", nounce_fin)

nounce = nounce_ini
bloco_hash = hashlib.sha256((str(bloco)).encode()).hexdigest()
if meu_id == 0:
    print("Hash inicial", bloco_hash)

encontrado = False
id_quem_achou = -1
contador = 1

while nounce < nounce_fin and not encontrado:
    bloco['nounce'] = nounce
    bloco_hash = hashlib.sha256((str(bloco)).encode()).hexdigest()
    nounce += 1
    
    #Fazendo o iprobe apenas a cada 1000 iterações, pois ele é demorado
    if contador%1000 == 0:
        encontrado = comm.iprobe(source=MPI.ANY_SOURCE, tag=0)
    
    contador += 1
    
    if bloco_hash[0:qtd_zeros] == '0'*qtd_zeros:
        encontrado = True
        id_quem_achou = meu_id
        

if encontrado and meu_id == id_quem_achou:
    print("O processo", meu_id, "encontrou a prova de trabalho")
    print("Prova de trabalho", bloco['nounce'])
    
    tempo_fim = MPI.Wtime()
    print("Tempo de execução:", tempo_fim - tempo_ini)
    
    #Informando aos outros processos que o hash foi encontrado
    for i in range(qtd_processos):
        comm.isend(encontrado, dest=i, tag=0)
    
    
