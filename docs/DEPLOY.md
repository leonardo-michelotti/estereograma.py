# Deploy — estereograma.py no Railway

O Railway constrói o `Dockerfile`, injeta a porta em `PORT` e só promove a nova
versão depois que `GET /healthz` responde HTTP 200. O processo segue o padrão já
usado no Observatório da Educação e no Sisyphus API.

**Staging:** <https://estereograma-py-staging.up.railway.app>

**Produção:** <https://estereograma-py-production.up.railway.app>

Primeiro deployment validado em 24/07/2026: páginas principais, geração de PNG,
canonical, Open Graph, sitemap e cabeçalhos de segurança aprovados. O ambiente
`production` foi promovido após a aprovação do staging e repetiu a validação com
sucesso; uma geração de texto levou 1,2 s no teste de publicação.

Staging V2 validado em 25/07/2026: Home com coração V2 e asset `v=5`, Estúdio
com mosaico padrão, páginas educativas, canonical e cabeçalhos de segurança.
Uma esfera inédita levou 1,95 s e o texto “3D” levou 1,81 s; ambos retornaram
PNG HTTP 200 pelo domínio público. Produção não foi alterada nessa validação.

## Fluxo

```text
branch → CI → staging manual → validação → merge na main → CI verde → produção
```

Produção nunca é o primeiro destino de uma versão. Os workflows começam
desabilitados e não publicam nada enquanto suas variáveis de habilitação não
forem configuradas.

## Preparar o projeto no Railway

1. Crie o projeto `estereograma-py` na conta pessoal.
2. Crie um serviço também chamado `estereograma-py`, ligado a este repositório.
3. Mantenha os ambientes `staging` e `production` separados.
4. Gere um domínio para cada ambiente.
5. Opcionalmente defina `PUBLIC_BASE_URL` com a origem de cada domínio, sem barra
   final. Sem essa variável, a aplicação deriva a origem do próprio request.

## Staging

Crie um Project Token limitado ao ambiente `staging` e salve no GitHub como
`RAILWAY_STAGING_TOKEN`. Depois configure:

- variável `RAILWAY_STAGING_ENABLED=true`;
- variável `RAILWAY_STAGING_URL=https://...`.

Execute **Deploy Railway · Staging → Run workflow**. Valide:

- `/healthz` responde `{"status":"ok"}`;
- Home, Como ver, Como funciona e Estúdio carregam;
- uma forma e um texto geram PNG;
- reveal, download e link reproduzível funcionam;
- canonical e imagem Open Graph usam o domínio de staging.

## Produção

Somente depois de aprovar staging, crie um Project Token de `production` e
salve-o como `RAILWAY_TOKEN`. Configure:

- variável `RAILWAY_PUBLIC_URL=https://...`;
- variável `RAILWAY_DEPLOY_ENABLED=true`.

Todo merge em `main` com CI verde poderá então ser publicado. O workflow usa o
commit exato aprovado pela CI e verifica `/healthz` no endereço público.

## Contingência manual

Um operador autenticado pode publicar a mesma árvore local:

```bash
npx --yes @railway/cli@5.27.2 up --ci \
  --environment staging \
  --service estereograma-py
```

O deploy manual é contingência; o fluxo normal é CI → staging → produção.

## Rollback

Selecione o deployment anterior no Railway, redeploye e confirme `/healthz` e
uma geração no Estúdio. O cache de renders é temporário e não exige migração.
