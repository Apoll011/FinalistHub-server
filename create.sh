#!/bin/bash

# URL base do endpoint da API
URL="http://localhost:8000/categories/"

# Cabeçalhos da requisição
ACCEPT_HEADER="accept: application/json"
CONTENT_TYPE_HEADER="Content-Type: application/json"

# Categorias com descrições detalhadas
CATEGORIES=(
  "Comida para eventos|Custos relacionados à compra de alimentos e bebidas para eventos escolares."
  "Aluguel de espaço|Gastos com locação de espaços para eventos, reuniões e atividades."
  "Decoração|Materiais e serviços utilizados para decorar espaços durante eventos."
  "Som e luzes|Equipamentos e serviços de áudio e iluminação para apresentações e festas."
  "Fotografia e filmagem|Contratação de profissionais ou equipamentos para registrar eventos."
  "Transporte|Custos com locação ou combustível para transporte de estudantes e materiais."
  "Brindes e lembranças|Produtos personalizados oferecidos como recordação de eventos."
  "Campanhas de arrecadação|Investimentos em ações para levantar fundos, como rifas e bazares."
  "Doações|Contribuições voluntárias recebidas de pais, alunos ou empresas."
  "Patrocínios|Apoios financeiros ou materiais de parceiros e empresas."
  "Taxas de inscrição|Valores cobrados para participar de atividades específicas."
  "Venda de rifas|Dinheiro arrecadado por meio de rifas realizadas pela comissão."
  "Material escolar|Compra de cadernos, canetas e outros itens utilizados em atividades."
  "Roupa personalizada|Confecção de camisetas ou uniformes personalizados para a comissão."
  "Festas e celebrações|Planejamento e execução de festas e confraternizações estudantis."
  "Música ao vivo|Custos com bandas, DJs ou músicos contratados para eventos."
  "Palestras e workshops|Organização de eventos educativos com palestrantes convidados."
  "Alimentação para comissões|Despesas com refeições durante reuniões ou trabalhos da comissão."
  "Custos administrativos|Despesas gerais com papelaria, impressões e burocracias."
  "Marketing e divulgação|Investimentos em campanhas de divulgação, tanto online quanto offline."
  "Impressão de cartazes|Produção de materiais visuais para divulgação de eventos."
  "Manutenção de equipamentos|Custos para reparo ou atualização de equipamentos usados pela comissão."
  "Pagamentos diversos|Gastos variados, como taxas de serviço ou pequenas compras."
  "Taxas bancárias|Custos com manutenção de contas bancárias ou transações financeiras."
  "Reserva de emergência|Fundo destinado para cobrir despesas imprevistas."
  "Eventos beneficentes|Organização de eventos para arrecadação com fins sociais."
  "Investimentos pequenos|Aplicações de baixo risco para aumentar os fundos disponíveis."
  "Parcerias locais|Acordos com empresas e serviços locais para apoio mútuo."
  "Concursos e prêmios|Organização de competições e aquisição de prêmios."
  "Consultoria financeira|Contratação de especialistas para ajudar na gestão de finanças."
  "Manutenção do site|Custos com atualizações ou ajustes no site da comissão."
  "Hospedagem de domínio|Pagamento de serviços para manter o domínio ativo."
  "Software e aplicativos|Aquisição de ferramentas digitais para gestão e organização."
  "Treinamento de equipe|Investimentos em capacitação para os membros da comissão."
  "Uniformes de comissões|Compra de roupas para identificar membros durante eventos."
  "Planejamento de viagens|Organização de excursões ou passeios estudantis."
  "Materiais para arrecadação|Itens necessários para campanhas de captação de recursos."
  "Estandes de eventos|Montagem de espaços para exibição ou vendas durante eventos."
  "Locação de veículos|Aluguel de automóveis para transporte ou logística."
  "Áudio e vídeo|Equipamentos necessários para apresentações audiovisuais."
  "Redes sociais|Custos com anúncios ou ferramentas para gerenciar redes sociais."
  "Publicidade impressa|Produção de panfletos, banners e outros materiais impressos."
  "Custos com energia|Despesas com eletricidade para eventos ou operações."
  "Água e saneamento|Gastos com abastecimento de água ou serviços sanitários."
  "Segurança de eventos|Contratação de seguranças ou instalação de equipamentos de segurança."
  "Seguro para bens|Proteção contra danos ou perdas de equipamentos e materiais."
  "Produtos personalizados|Desenvolvimento de itens únicos para eventos ou vendas."
  "Controle de estoque|Gestão de materiais e produtos armazenados para uso futuro."
  "Materiais de construção|Compra de itens para montagem ou reforma de espaços."
  "Outros gastos imprevistos|Despesas variadas que não se encaixam em outras categorias."
)

# Loop para criar as categorias
for CATEGORY in "${CATEGORIES[@]}"; do
  NAME=$(echo "$CATEGORY" | cut -d'|' -f1)
  DESCRIPTION=$(echo "$CATEGORY" | cut -d'|' -f2)
  
  curl -X 'POST' \
    "$URL" \
    -H "$ACCEPT_HEADER" \
    -H "$CONTENT_TYPE_HEADER" \
    -d "{
      \"name\": \"$NAME\",
      \"description\": \"$DESCRIPTION\"
    }"
  echo "Categoria '$NAME' criada."
done
