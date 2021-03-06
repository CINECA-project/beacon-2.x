
from aiohttp import web

from .rest import (filtering_terms,
                   info,
                   datasets,
                   biosamples,
                   gvariants,
                   individuals)



from . import html

# only for testing
from . import test

routes = [
    # Info
    web.get('/api'                  , info.handler),
    web.get('/api/info'             , info.handler),
    web.get('/api/service-info'     , info.handler_ga4gh_service_info),

    # Datasets
    web.get('/api/datasets'         , datasets.handler),

    # Filtering terms
    web.get('/api/filtering_terms'   , filtering_terms.handler),

    # Schemas
    # web.get('/api/schemas'          , schemas.handler),

    # Genomic query
    # web.get('/api/genomic_snp'                      , genomic_query.handler),
    # web.get('/api/genomic_region'                   , genomic_query.handler),

    # Individuals
    web.get('/api/individuals'                              , individuals.handler_individuals),
    web.get('/api/individuals/{target_id_req}'              , individuals.handler_individuals),
    web.get('/api/individuals/{target_id_req}/g_variants'   , individuals.handler_gvariants),
    web.get('/api/individuals/{target_id_req}/biosamples'   , individuals.handler_biosamples),

    # Biosamples
    web.get('/api/biosamples'                               , biosamples.handler_biosamples),
    web.get('/api/biosamples/{target_id_req}'               , biosamples.handler_biosamples),
    web.get('/api/biosamples/{target_id_req}/g_variants'    , biosamples.handler_gvariants),
    web.get('/api/biosamples/{target_id_req}/individuals'   , biosamples.handler_individuals),
    
    # GVariant
    web.get('/api/g_variants'                               , gvariants.handler_gvariants),
    web.get('/api/g_variants/{target_id_req}'               , gvariants.handler_gvariants),
    web.get('/api/g_variants/{target_id_req}/biosamples'    , gvariants.handler_biosamples),
    web.get('/api/g_variants/{target_id_req}/individuals'   , gvariants.handler_individuals),


    ## HTML UI

    # # Auth endpoints
    web.get('/', html.handlers.index),
    web.get('/login', html.auth.login, name='login'),
    web.get('/logout', html.auth.logout, name='logout'),

    # AJAX
    web.get('/filtering_terms/{term}', html.filtering_terms.handler),

    # Just for test
    web.get('/api/test'                  , test.handler),
    web.get('/test'                      , test.handler),
]
