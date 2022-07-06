#!/usr/bin/env bash

# tenq ter .env pra puxar key

# ideia eh dar a opcao de "Batteries included"
# Pasta do Projeto
#   |-pipeline1
#   |       |-pipeline0.yaml
#   |       |-pipeline1.yaml
#   |       |-pipeline.conf # configuracoes gerais dos pipelines
#   |
#   |-pipeline2
#   |-pipeline3
#   |-.marvin # avisa o marvin que eh uma pasta de projeto
#   |-mrvn.make # configs do compile
#

marvin init --name "Projeto Ouvidoria" --clean #--default #--tutorial
    # --template "python"
# Cria arquivos e paths default no diretorio atual

marvin config modify
    # dita como o init funciona, criacao de templates

marvin add template .
    # adiciona projeto atual como template -> seta variaveis de pipeline default

marvin pipeline compile\
    --pipeline_file "./pipelines marvin/ouvidoriaPipelineTRAIN.yaml"\
    --config_file "ouvidoriaPipeline.conf"\
    --run_interval "0 0 1 0 0"\ # crontab format (opcao mais visual no arquivo.conf)
    --env_file .env # keys e etc (sinalizadas com {} no yaml?) => faz tipo docker-compose
    # env_file cria warning se tem duplicate
    # compile cria uma pasta com arquivos referentes ao pipeline
    # inclui configuracao, inclusive intervalo pra rodar

    # passar o arquivo pipeline_file ou o config_file seria pior,
    # ja que o ideal eh utilizar os arquivos dentro da pasta do pipeline

marvin pipeline Make.mrvn
# re-compila, make.mrvn ja traz as configs do compile?

marvin pipeline import --txt "{JSON}"\ # pode passar diversos niveis (pode passar arquivo tbm)
    --internal_path "component0:component1" # == --internal_path "0:1"
    # esse comando importa o component do JSON para um novo componente entre 0 e 1,
    # re-numerando a sequencia seguinte

marvin pipeline import --file ./decision.py --internal_path "1_0"\
    --input_var "isNovember" # etc

marvin pipeline modify --name "ouvidoriaDeployPipeline"\
    --internal_path "components/component0/envVars/DATE_BEGIN"\
    "05/06/2022"

marvin pipeline modify --name "ouvidoriaDeployPipeline"\ # opcional, busca no dir (igual git)
    --file ./decision.py\
    --internal_path "1_0/conditionForActivation" # pode utilizar os codigos 0_0 etc, ou nome (path) completo

marvin pipeline run --name "ouvidoriaDeployPipeline" --verbose

marvin pipeline deploy --name "ouvidoriaDeployPipeline" --verbose

marvin pipeline ls
    # printa as keys pra ver as paths internas, ex:
    # pipelineName: pipelineOuvidoria
    # defaultParams: {bucket, image, envVars:[5]}

marvin ls
    # printa os pipelines atuais e informacao basica -> docker ps da vida

marvin pripeline draw ouvidoriaDeployPipeline # desenha o pipeline em ASCII


# Persist vars for next step, may be saved as json in minio


# two yaml (min.):
    # - first for all components
    # - second for describing exec order
