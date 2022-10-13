#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by lizhiwei at 2022/9/21
from hashlib import blake2b
from typing import List, Union, Dict
from os import path
import sys

from pathlib import Path
here = path.abspath(path.join(path.dirname(__file__) ))
print(here)
sys.path.append(path.abspath(path.join(path.dirname(__file__), "../")))
from apsi.dataset import Dataset
from apsi.server import LabeledServer, UnlabeledServer
from apsi.client import LabeledClient, UnlabeledClient


import pyapsi

params_string = """{
    "table_params": {
        "hash_func_count": 1,
        "table_size": 1638,
        "max_items_per_bin": 8100
    },
    "item_params": {
        "felts_per_item": 5
    },
    "query_params": {
        "ps_low_degree": 310,
        "query_powers": [ 1, 4, 10, 11, 28, 33, 78, 118, 143, 311, 1555]
    },
    "seal_params": {
        "plain_modulus_bits": 22,

        "poly_modulus_degree": 8192,
        "coeff_modulus_bits": [ 56, 56, 56, 32 ]
    }
}

"""

def _query(
    client: Union[UnlabeledClient, LabeledClient],
    server: Union[UnlabeledServer, LabeledServer],
    items: List[str],
) -> Dict[str, str]:
    oprf_request = client.oprf_request(items)
    # print("oprf_request: ", oprf_request)
    oprf_response = server.handle_oprf_request(oprf_request)
    # print("oprf_response: ", oprf_response)
    query = client.build_query(oprf_response)
    # print("query: ", query)
    response = server.handle_query(query)
    # print("response: ", response)
    result = client.extract_result(response)
    print(result)
    return result



apsi_server = LabeledServer()
apsi_server.init_db(params_string, max_label_length=64)
# add item 
# apsi_server.add_item("item", "17890item")
from hashlib import blake2b

# hash_item = blake2b(str.encode("item"), digest_size=16).hexdigest()
# add hash item
# apsi_server.add_item(hash_item, "12hashitem")
# apsi_server.add_items([("meti", "0987654321"), ("time", "1010101010")])
items = [('JRIKrInSyZfcBADbXigLiGnHisxpWrEctHEQzrryFjAHFoPQAjEoxQhTPoYgXIFI', 'GukbcSbVKQheaIWdNCSszRGwWEJAWTSOPfeTyHqomeCwPehKZHUEugDMxyXtaJHg'), ('HhiNOgrbShPQUqEdCjAkZaOfBhdGqUFdpNFsmRKdpBFLgKFsrCIjOKIlobutzPqV', 'jyqIZDRXdfYTMWTNfYJRokKEAuOPgTYDmKwMMVyExGBchzcWILkClaplKvCLcrEr'), ('EcMACQLbIQwubNYCIvEMjvXESNcbyGsUPEMhzLIczwSwpronsTwMEYHqvKtMtXao', 'KvnUHWxkGUxvVoEEDBinIDjqnyYAvoQUSNSNtgOFkWZbgEGCEJFfsqlnjQlcowqx'), ('EPNFaeHqsSxWGmHIdqOzpnRDVzUJVqOSqgsHSDufrRDFUSCxxLEOEcPhNimjUOnu', 'cjVUxvEihWnbDZSFzOxtjRUacvKEyLwGjPoQoRwmsoVKXYanGLBNVGODnPsixNML'), ('SNIlEMdrOTmfjRuBdjtOZisftxSDGaBiTgVntmzklfjlljytAAfbNSTkAABBBkej', 'ruhIbuUIxDjaNyTWKlLAepHFWKdpcKgNjpgfxPeVHZGIcIbLuoSEnHYgCQeakspn'), ('QBkorLfQyJlpCDscVZtNdvjjcduCDVsFmNMkRdvrWjxFVBdWUALbYZAHhxOAkXzs', 'eaPopQrEWFJoVVaXkFPzquvYToKMsfnkvhEZpjZtmaERUMQBNTNhUcvhfGRDEUSi'), ('nbFfUZfxPbixidHSVsCbdmvyhuSmsJjGSvdzCgPTOuWgzDoGZGmQXulVXXZYFfxn', 'zOmZURrdOKWmNuHFHUrIPVVMfXHngXCJooTzCgSXiNsYgqUxKocvLhpGQVnPVDhT'), ('BLyPhdTvJnaIBvmCerEdmUOlWFzXEbLUiiLWcUgFpXWGCmSnamkQVhuwTdTfeVED', 'SLOhmDmOlOkOrheoJFcSFDjMPnclevWFpYuYZAgrdVPhCNWpaabGaNYmJSdYoOBc'), ('gqkTVkSMUzpSICVbIipCSqgerpYyszSIxqRlafmSNvQGvVeiepBSnJtpHSVXoBtj', 'OPrTxiPUmBTiiWIfoMerLiOxGWqmcrproLSymqbPRLGBUiHwTUVgxPVbLCRrlvHe'), ('LsgWhbKlJBgFcHtKbkQZSWCwTxEnknuiXVKqcgkNWrRiEQZyBQGvMBSliGxsISeI', 'AUAPxwjgIHELnMvKvMsCkkQdJdwOoZuaoEsXTLvOkOjRxakSenIKwURHQislnkPU'), ('BkMOcEuIEmGWYZsbkCQHdyvSWgNSyHzZJdtUGiGBVdQtdhKeTAHeznXhWKiPWPml', 'bbTJoyBJMxzRsNtWnbyEdgePrWuyIylhwfRdKqwEViijdtCxnlDeYUlgxInbUxHs'), ('rNXQrQQzOqwCJmqxnpsvlzoKjLoOIfyATACVceXXaXpKutYuKfvlGlwfUOjWwCKy', 'sznQhLRvRLBGUQnnGHRUsKrpALgcMuMhVbKuJfbZllDrzqitLiecBAdgRCihgaRy'), ('QAlpegfcpxHlsXzopOhfMMeOswbwjJzKDcbTlOUKBcqkdaVFAWfJivDwsAGtzJrN', 'xiCFBayTcNzYQWuitbwIWbOIugYUbLMwJgdNdYBlBQQZaCDgOVdOkaCvwruGezgI'), ('nsyrwPCMFWWgIXuGIroUMZGyQvidzXZsOFuXXMYuPWstaSurUJsfvnjkFEpBRESw', 'OpHDSeFoKbEDkKRhpaFNdwuCaWFaAWIZKCjwVxQdRMZPkPasCONjfkuzujzmXtCR'), ('GLeIyWotbWxVHuSnQHOyfBtCvDTqsxFRWkikyqsnEfyAWWykLHLzXNlXIDryWAnB', 'cXotNISHKKJGKhqrnXdjHLPHOHtVfkcHkFGMPLntjwEuOeHONvNkhpQcRhLNHKam'), ('sUjHrXQGxxALyNLpTbwPnoHSrPpAqZJfKJhUPMEjcjCgwqbNsTRiGDGOFsejnQjM', 'jPpPedQzxqnVWQBDFEKNMbRRWumRAjlpRYgiquSZbyYWospuJtExiNaRMOXPtCzU'), ('BrNjYhUWDBXyysNPCXGJgZyrYZNOJyVUWyTPFvCEAIVeqgoJqBSgGmcKjbIKpaGn', 'cHSWuRGoKIfmHkHvFKjDixyPCzttKJIbKsJjsRxKwxNOksgKqogtLrkebnViZUFz'), ('CyvviFLTIBMLVCpuVSaxWjUweGJmzhEfwkzsXBtaJZtEyvvsZCSiNimOSloSMxyN', 'ELiisgnrvAKDUkKaojPnUOGTGawgbIlExLeNPOOIyNxKhqnFpHwyxLQXHKsNrXpK'), ('KAruXkeHUWbQgLnorfrHeLhhTBcOqczrWKzmdKcpVWdJYqhlOyRgTVoiupEdxkSN', 'NhWQeKOEOwitrfTQfbBUwuEZeLcUTnlISMCKuWVequUbYYhhuRaObWmayCusVgYU'), ('PNyyWkbThzBQrMAQGmTgChQRwiRGNJDLFaeHKPEmRHDZeTbSiOFukbZhjjGppowS', 'kbdiDivEPUjNwTAzTZRkyjkfszctzTafhsiMsIvSAeHzfwSzRxoGwMnDkJyKsWZk'), ('AYBGBSPBIZNxKsgZmKDcqdPoXajfgPigtSecPJttUnbdjQbtZhJDpeJQHzFVYPRR', 'jvppfutUyXsAyzWzMBOAZdShLhprytCEmJSAVAJjifLkbmtYzDDJtRARfRAlaUAG'), ('YGDDBQEtAzRzZIzNxBPBRtZHJqQYhAiVcyTXwOkMmFpoTkczEawNOGpYKqLoUrlQ', 'fYbjLudTrrmmRasZwBSCQPspLoCXZDdaimYWZRnQKcPLvCQBhOjeEbZBDavxwFeZ'), ('BSTdpYsQcWUzhhJwpRfzyupsyFSQTlUezPTrIDZlCQCnjAKFpqblDSVCJMjYlqaD', 'iuQwjZMVQstoulpnwtzhovHiLXSKUQJKXkcOGHMNMQxYGtgxCLTrNiUjWUnVLyDt'), ('woBiskyUTDtQAcTCSIySkcxWdbuodzGuBXtjGHEGlbBgHVBRSlqUQavWSppHqkyA', 'FUdKUXemaljyhldtQqzUVIBioQZCkavjpFwubbsQqOPLJwRQAYAioioOLBBCpjnq'), ('NwsdtoftqxomFewAcPXVZDeNbTCbPQqpdkpvEEOkrLaUNMogEOUououHWmhDHFWA', 'SudvHwUEzCIiyCDCQnJXrRYRokzhOJybrfoKFYovWOcQXbWovRAwWYXoAJWBlJNw'), ('BXVyjYYatsAlaWRzNxOwkfihJPofakhNTezbhFInOgDJqAKgxRjAbIhQWUwnJNwz', 'UIfEWlBXXCDHUmiBQVwLkLklEtmNiqxbuMsgwiNXUPNYDSjhpeZPnALONFeBDHmo'), ('TPJWFQuDWhUMTGrzjdemmFEGYnINpSrjzRhmLFcdeBtKzHDOyMqjRtFhNqVupeng', 'brlzBgbFTHYSxYedCJAKlmsRDmqyUpVykMtDZZodXPmdQkkyZnqjbuBdLwzCVSQN'), ('JlKmAfeFovGMmYRohwPPPBIaKwUqIxqhlJZQPIGxcTcDlNASktFNvbqqZkIeAUHp', 'tnuUhryRlToaGTWShWBKEfRZsacqECwIiJyeakxUPuMTpIgbWzvKDwKoYmgfCyzY'), ('LJNuLicOeEIdRzzLXZAXPpmVqNNRRSbOJMoFkqZWrzWqYLagWwYhkHBxaOVCmjBu', 'vabchgNWLBoULKcCzOytrRIlsiogYKkAdReTKlEbitvuLhnnVEoaIvCQJmpDBLtM'), ('EjnNXaoxnokyUshDbgTNxwgZPjTLekjoumfGLslquJSPSllBPYOBYmZQgdFagmPF', 'MhEzifGGFEMAhuSEQODiVyHAarwpnEpQUePTlMqluhDeUODKkzGjltvwgRgfqhdg'), ('NkHJecljNMPKZGZYbHOYJhpvUOCnTmjHATTtBHSAgWESKPETGoDlgQfNPhBeMgNz', 'oSGSvfRYUbOlVksILGvWLaumcKCVhGpoyAOXmStrqfvWmuPmzAXAAeSoKzfXYpNM'), ('iEfyEZlWNiCAIAaYtUbAsnvuPcyDBCSDoQypqlXUvRxyLFlLzeIMPmBlZraTguCK', 'jAhnYXUeNcYyHxntcljVQusilFpwxOtAlEhqpjhfHCxcidDkrwtUSTrCHDgZmgsG'), ('JlAGROhxsybKaKvZOXSiTKIqsmkHAGExjHJKAsPdBDjCucFylpWvcsNqDIRYEXKC', 'WFAhapUNUCnsHHKOeBFgmnnGmCFxsAxjrmrkHdRsgkRfdzQueAkhBjsEndznOvJx'), ('pmfhKIrAqLOUzaEsWTppLtGeoeyyVszrSIRszMnXzbaCtTHXzjnwcbsCSXxDeQVn', 'QBPccnXgoQhCjWPMPFNdvCfzDuIUtsSMNKUesGVyHkbKsBDTarzslKkdpoBBRAIh'), ('JwXBtHQGuTgOkHbmwEcSaqXoDcDkMMNuuZDJOXlMustwsYUtUgFdQHnwhmEngjjJ', 'OeoaUfJBSnLBWMPLbTLtqYkUOHhRZADIDKxlUHRSiVFxGMyrpJMRAZhPeaaIZXQq'), ('OWmPlfeRQSlpVSywpjXjBmEITrBdKuGzYXAgmJRBvUtdRmUfljRJpHtIQFqQeuTJ', 'RcDewMUSnyEOHoeozzcpAFgAPLmodbjTHJhKbnWfeYuGBqCHXXwJAwGvPTWfSsPg'), ('HBXBzgLCYmAdxDCrEKSznOgEgTPOdxlmBUVbdxtdOHbqWhXefljDDMnPYCRjUihl', 'sWdBqjmVqKgUxBDCZXojfVSOubomXBIuEeJbGzaZGJUyQsFMqZWBBMsFGooYAnAH'), ('ORTkpSCFhFXcxHKVFNMqtCvXzORHolFGblkGbSowEvxtIuZwsZKBdwcksYZMnrnY', 'ksDhYIKdzScHMxrEXaTrcDFkFsFYwtXeTsYVkZjHgmMXUGZnLxbXiyvClRTXbTkG'), ('qxZWasRIyinOqLdHNzZYylrSnDCMLdXOVkgmbXxQCLfsExgoCTKwCSjUEzJwpSOy', 'MpZbSubPzDkYGQSwSHrypmhcSADCNrTbHGQiyFwiBDhZKCuWngPwmGAxlZruwRyc'), ('MFDafMKvfqPHMJatFkcKsyWALreiqGbHTYLXxpFElLhKihLfgqoofIYZcJmtxrPT', 'TEESjCbDwYfvGRMmRJkjQuUsrIcrwxFoBmgTPbZbSaMwqlgIhuPoFvmTumzFLfpp'), ('rNyzqrZImLBJYlPsjVTWXyqnfuVOoKTXbevxAqaYkURkFiYoVzrSITsSPgKMQfqz', 'jyPpSbAGjuoaFaLAmVAzmrQweHqHgvkEmsUnyjUmkdCmfLFGKwSXThZCDyWxAeQG'), ('PiopYzjpBcbZaTQNzxWzoIgCddBHPZSALigfRkEoZRUMWTwnbfWJZfHwSMUEMmqV', 'KKKahpgipWitPDsUdakNXOWCCCOTroCHhHngGRZCukUUfDrpIjQQGdWKdWXtvHeM'), ('aorCwTksAxNbeCAEVadqQlgeSSOJFiMxWLGZQbbTCZMDDCqhMXsvoDrjRopqnfjQ', 'kTMZySYENzVMzLGqxnUFLwBDQlaDxBgudiWnQVswvMdlkshsdVcLALZiiKxykerY'), ('CEVjSlThFxOsdeAbQAsYanWiQtSZREJauxAURbLLccVxrPzvdTDXTheBtEtpXoqz', 'FDpLSQeZvTKgEyvDwNWzlUnnnXboBOAidSxRomzFUDFTjMMazeVhVmHRhADSwtZG'), ('TeKVjFYpTnBKoeOmRiOeAxAwEDaEZtQySDmqheHyYwLlffcDcWTDnAetajwgljyP', 'HkKjKizseIZhhxtAQyYViKepdomOsECVJYLIzSIuSODbmLwbidEXzkVrxxMOgxxk'), ('WppSJlLrYsAiaORFbfEPgPxDZxiCqvQaIrAOkhGWSGtgMTBaDSpcryvhkqzjEOOu', 'jpmNUGRfIRGgNliWZBTExlVmPzfpofOKYTlkiPJgicpMNanhLWyMRaElcukiFGHN'), ('BAATjHjOerPfeXusqbtMHieDADmFkjjDwhyuMeuAaIbXHQllTuhfgDMaTmIfGESl', 'SEUtuuRkHxJrSOgroPymkruYGytXdCNxIOyCAntNfITHVoxRIFORSPeCiWaGMHZx'), ('oVZCxelzGZmvIRfNlkknDLwEsShSAHtrrJQudpqZFhEXkHgPRaUVTCSudFslOHRE', 'fuaazmrvsSMrpSjfLNQsAlhJHpVIDCRRuqFYMgioUnMbkVIOgUfqhEXJSezkJyeW'), ('CsggEKEWTZmPluDcZnZJlhrSXWDQmCkyOPIVLSHOOJanMVqceFgImYPWxhlWgWnI', 'KabqrTGOGBoVMwxoWUHpaYKIhLKGAYJzBqDUofdkxgrZvviVhitfNgPkdAGEJadk'), ('DAYtwrmButZfhqdEVNeJhtKghvSFUJpbvzFBrdTURDFAKeZSmRkPjuvJgWuVHqdc', 'DyvERDvYJjcLFeywKOBpxbbBKlUdJGLfTQdmRFcNLsZFkRhPuTjPstmCbnVonmiS'), ('dgVKypNKCJWOgMBbCxmdHSnJGVEEbVgmMmuusviHdhzONkNYaQiuOLSnhrHXuqTR', 'ugPKzpGkEfcIKGdOHLHLUAqqIRBUzuFDrlenEOnunuJZkAhkFhefkOqFRpynemER'), ('TMvRoQWJdOvhzPceWWforheVLYxhysOgwVNpAgQpQsAvXxOzseNmAHVhmfbOvcVd', 'FiJcUAUotmBfRtPeUYmrwYDjqjYItWNBhMHtCLGvDqqHbUvgraxpabNpmQXkOUlx'), ('moADaJQkOklnBkOBgavNsatYYachzWswQgVuHKSAkEAmZLSEbqEaXnVKVULQBAAX', 'xEupWXDFJxHJyyBLdKrehFKHwXpzHABuWsSnqvjMPJrqMWDYEYqDZgTkgXyqyZxG'), ('BaxWlWXvwpcPTdBEPYnxNYeDpLhsYOSLyvgKUXWExVYSDEBIXxwbAAwfWkrSxuAO', 'EVYRsujBWnGoqTIaTJuVefepOkxBMIpdXstssPtTwFPIFncBIMPiiEbwmntIFYNK'), ('sKQHQvmRsGfPImyjDGMZZkJCUHzRPJKUjmMrfGdOWyiqRVqZbxjCBeeKqVRtojpA', 'pwBqIoliegYtIpWqFzKONCTuhbcAKxCtVsfOnfmXhxzfijJZwVhGxWXZSPmpQgKy'), ('poCGEPcjGLmrtTHjvesxEjRpsuwPchFmEFRxoxVcYbbIchVqywRwKLImeqEGORkb', 'fvgaXEdgAxKXFOdFSLDYgmmyWKukRHoLverniKmVGYMFXcydbjwexpnBOPCrjaOU'), ('uLClBeEvfwRtStCUQuIcpiBUtdgMybPODiBTyJKcdAzFiVbzNYFMUbvVyRsMzwZS', 'bXtqYpXTlEbFXEoUiUjnJCLMXtfaYKReZIFnFKGcyKmDwCaiplQrjFtdAclBEFLA'), ('mwxaoEzvISGMnsHPafnDdCHwTeRsVAZfSYCXvtTQawwIhYaOGzMUWvIPecwhZOiJ', 'iqFqtFVKHdaGpfHzbhjoUHXGEQgsqzgKuOVGScFeZVDjEwREMEksuQAGvnPgWZMt'), ('fopFOCOHbGYXahMbLedEClSohlfAyzVAjPHyuRuPSxkmCRrzkBeQOTZyIAfiQBmK', 'MoOjoDsQpZzYjjaVwOMxkjWZkjIpBtNojSytrxfADQOfvmZXJKDFgNzcpCEMdwyj'), ('aOZvpErPqmCSTPLhfDkjHvIBeUyjCWgUPpTTdEONvaSFhNpZDaoRZVqBnubRYaGj', 'uHWxHmJKrDDmBYaFIXSMfpnGtRTPawzniypKVKKhHGkEdhICYHtZkkQRlGgMhEbo'), ('GWjyWPeDoyjDyumkYrrCfEUjsiYCiqvvNYjWlVXSIcCbDKoiemUzIjnmHFBIAHWF', 'DuZinZmnDSsvlGecxhexoTIYqATisSjUnyOoQkrlLSmUWIVjaqvsTneaizhGtOWR'), ('flkjCKqBPRIypbEPTSJRHZbKKerlcrMzCQTtCpPUHccWFurGCoypuyntfEObjZSn', 'wGzsOTMQZkRbJMLEGZBgBSAbGEzdnisLXyIyamRzLQmsZFbbmLyeObLsOQtNBiJi'), ('pRpMrdLFOHwMbZPaDXxDiWNBtWMcUSQhhXxfpaLQsnjItFzRkbNkUNhAXtqFGwQE', 'aXtwgeqSESWhCdzLBEwBIyGYRMyGgtedbDqxVZjylAxPoEmRNvAgHmHCwjCNFcWD'), ('ZSXnJdJEgqxhJWdcdRSajncLJRLqFqzzQyGyftzfKUZiYQwoVUTKskaRZtlSCLjB', 'rLfFJvWUktgHJqOJquUfmaMDJwOYYxkOxHaOyaoSyWPhrjWFLXEnReKtguMCwlYo'), ('NxHoDwizIUdCaquEAcuDyVsNbCsBzmXwAKnmVvBIIdzjyyRnIPHgYuuOExeTUQRk', 'jODjqeUwwkveGDxYXlSqVSnbiQrNmLobnDfpVZLOQQPqeVGbIOJrAycsPXVqkDaC'), ('yyclsHHZBozkuMHvYITThfdSkiYsCytnCstysLrmPdyCkJIqQTDadYRzvosBLoZc', 'ACifsTgJEGZVVJFIqOIcVdfflwjzjbqqxkSNGfKCUhhIDAkbyEJcqaCGuKxYhDhV'), ('qAurJRVjpgyWwNmWWTUZgNRJyvNxZGhzDpGDTjzZPTfZRKBISuTsyQIKXeobETjx', 'dLruuWxVNiJarTvEJCzvhNzejxVqPOpnaaAMPcCILSjvtMVATMZwqvRkeuoWgqfe'), ('FEVwndZtvKFUkLYpCbNneUageffLmPicvbirNFwLHlvdNoAkqNWrqWqcYkReCWST', 'HprPZkVLZauFbZrqFgsQpiCaNBNblZFZWAedzmztpTJrdgnRWYyDXNJuAKpDOKBY'), ('ZAYOxWEeqWvuNLLEhCtBcVcXsmZPyZcmgEnrdZZvSEmlLPxsUnzYkAJCuwxOcYoN', 'gDcRckwuVPOsIUJiaITNLAupXpJqyOhczDliaMOkzdAttdyspskAtnwqmAtTwdRV'), ('dhnlMIVzVIiePwRtwGAtxRkrMaKDFAuDbRVRFzikuoFekvtSFNrizgymFbxCnhZI', 'USgfiSZrdZihcfFXcdZIWLolgNmsmgInQYtXxMiSTuuuAxbqiNOaTZyejhivMBxe'), ('AltnVgyOPeydLYTQnefMnfCXmIyIwPmVzwCoBaashIOvgyFgUaGkSmXVwlJZzcUM', 'zriHThJSkLMYJoiHfscUXqoQPJmiohrzeNXUjGUlgOWoAERkQGUGlwpDRZosGpXY'), ('tlorOwLrrIgYzswHeXxNxNUUzJMTeYtWJWEskrLyiMelEshAamnjgqsBbftGhANC', 'YqVHCoegufQGmYenPLPdowKUdecbWpnMGRAvPVzIucnUulpEEjFBVAJJeHfikAjL'), ('mHjAMyYxVUOumNPmfzhwojYZsbrwmyrWqKInBVJQYFlwcImBiaOvsDHgIvHaNOqW', 'UwDwPfnsWgmZWJfXucKCJfAQClmAhiUUPhmKIJIzODtPlKdJhMnupYTNbRaSAIgS'), ('yUwTCFvyGCRSQblgNSJSiCFaEARHcfgDvrXCLDidxbnnIECJtDFNnLqFwwpfYnKt', 'wBeacuWktatCqVQoQSFycCPcUvwfyWngwGFevGHRyYrEeeLrlCjDNhIcWrEmujTQ'), ('NKViHhYMNxoUDzunEhbCqrpnuJNJSEvROgdGPtnrXRCzFICRrtHJOHnpoCUBtxPy', 'jQdlIzbKaZfpCYnFJvaJRtSeFyiaBpeBpmmxYbhHxvZGxRZaYtqQLKGVpWdYuLlC'), ('TvBXOqIzsFmUtlPxHZDYtQrmAWMdxfKmSdGvJbydlILZQKiwbxtSBLbixelGbAAg', 'fgbZDyazseoaLEeGQgtLNHjimQnSXIbjDUbIdzSGNieofkXzaMQZzYeaEjxgxpsc'), ('zRoFeNpZraNRCVlRkHBDgyAtqRiORlGDslUASLFUXMBTqAEywmPhnGrMQYzHhZjC', 'pUjhfWqiMlYBstcqqNkxtwVnPCplszVdieMPSqLfBPmzhtEYsKtHzpvkSbUcGBbQ'), ('cyVVQLXCjFHYUIuXutvQGvVUBnVdgsDOOwHmiCEFNGiIQOaCJzSRenYBeIqIiOcs', 'MEEeToIPTGvaiTqGKpUshbGAdXIuQzTpMDOHNtXefPAgzrTCmTmJUQxozsTJnJcX'), ('BPAUhcTNvLIIWsVCFnQAmbffdEahvnBABxFiGfAiUpClnJwGdUmmyicvfiwdRPJN', 'RIWTnemDvPgAWXshfWNLrkQTpACEkLgKjKBApPtIexGzidZWgPMyfSEaJoHTxQSE'), ('YxZTcxyLqnPfBCIAddkNpxWUxYNqjdzaVHpsdhAibBpoaaCSGIANuECkhScSCkrT', 'FeZSiZuljZwXJocoBlXWuGnrWTzOPZjrGOywocJTiRvokmZVcjApqcMZJpJLZgil'), ('fCnUVLmldmIAuyCApbShrECkvnLSOKEDpULPhAOsmDhpLmUjuSKgyKFKCiJaszUk', 'YXycpAAJLWnWPuXlAMbZpzKrbtMbGkgSYNSbHiEfyeOmAYHshpaLGFGOHAQvnWZq'), ('tsYTttDEMIlpOWYRrllvPtsvkcUWXaGkvdPlevApgywTuNkUSRlRHJQJDVcuIgkM', 'NZFxuaJjvLimVPQjBncFfvcjpkSBkjOHcseTQslMLfdBMAlAuKrgRcYwpngrvNLm'), ('SkBvLtYaIwekkBxTPvLGENNAAyTScRVhKeJYMpIyXmsuQwrCCySjOtolsCUdmlAV', 'FyOlIqPeHXWiwUfghwGLwhfbHIveuLOVFiFhQMctqdkijRYEzXmhIwVFWiEtLloD'), ('tsUtIGXECHJBOVaObHtiTvKkqUGBZwkcZekbzWECGcjmJPJDjcwwienBaSZAcjrN', 'LZUOPgdAVJAcihJnbroVZZJUHaWetSvATCWWkVOlqiCorOdQDBahUsplCpORiJZn'), ('AdVlwTwnsREszEvgxUViElZSTftgbIZkxeSDPTqBICvGdCHKUFgDCtvSDCZrYPue', 'dHBeklOOqvRbvrjjsRIuhgQNrwXCOiywkrOuBIyeekhWYCSlVNQusUsXKgvowZIw'), ('jOTWSwSVJvRoJCdSnZfjOMjyUPZbltgrwAberkRkLtWVZNaViHIGBidCibFdoJEP', 'sRqrSELrNxtGVprCzMkOQSzcsWFcwtFsxphqvTkcQXHTneuJyYXFOtGeuUOIANXU'), ('mzJcFGTPloqefQGkOmjkwWvVTBcszpVRjMmRUtDjfbXfJWLpueczlWlEvkiiCtqz', 'cFnlJcIQEXKpDaSeXVMhYwVxUkQoKTNLxmPbWTHcmRGDtRJDmAReyurgyBcaIiXo'), ('TEDjWarOSDXJklQMNVBRruNfqhRgkTLYKAHeuNmNJkmsUYAxxXylbwHhnuDQsyXM', 'PkKpladRFjKCzJznyCLxpvwyHbXxksrZiuRyQNJSlJBqCzpwuhgRMvXvAMXUPxgH'), ('pxUADUaKGqhoULmFJDhbxElprAvaspdYtbnybmSGbWkBKhSLttUtkCzEOXoTcyYH', 'tUaEtJYUuXudjREXrNYWSfGTzaKyzgVVEdKpuyXrCBsKcrWtTztrNoYtGFgfEzRK'), ('DqocuptrHLwMzVPcnBdctnJaxlGwLgWLdLVkOmETLiOrQYXNWsmAggjLZGiOEgiJ', 'pVSCNWiMIrqLRiMoDnGMCyhMPkVlCRWWBFjZBhxqJIBrVGbDOHFutGFXYmHsvdfa'), ('uadJsIYnwygSMSZttQKwPSXtTQulpSHnrbxRBcNubWBphusfzycTTxNUHNHlSwXd', 'WLUPqDkcWcfXjmzKPadGTFiGAGUhzKxwcHyDqSMXvZOaBxymrNMYESobcVTKUYGr'), ('GuVEvQSyKmgOhlehUrZqrnfoSyOhyYQdoopZNLllLtUKpIVLWtnnNDJagOVLzwjb', 'NFGZIZVQUaYdkgwroqrnOsxHOsYmyjEarclwUpinAIpuUjSxKOaTPPqtcuhpGUdc'), ('BFpAhGjLvdMbQWqnbmRlsetaKQsibqaTLlmwdnMxWGHwnGnbOQFbNGWHwujVadJa', 'mCJpNxqPDowCAVYrlLpvbZpbqVsKarJPqGtKrqLCQKWOENwxfeJQGLNEXXPliqgn'), ('JwraVkItXySWmnMcEoNrAcjWGxqBiWiceAIEVpMYJGpBzIhizxNybzRmlchvvBxs', 'viJxXEMnACvIVcUsEGergCYFPFyPzjpKRwumwiOJdBJqIzLsSIROgJvCAYMZSQNH'), ('JegYmPISVLUEXgCLVBCfwNrskNNniCJVjehiRBMKlHpdDLhnOggLKLFGwMrhnPOq', 'szqmgMbovWTdfKiMlMZrKcLViKwNjVASiFpfOegJxWTMsxyfEuuYuuaKlzJhiLst'), ('EGlvlTcJaurvWGklIuYYKrRwfuCIXnIVgVmvEMnTbmbxzNRIgXjlvLeVzvBegCXm', 'mjJIApLJzPPFUMXTzCiggjMOjGgdnjmSrjidtObJDGIcCtncsoRZfLbOBgokiKYN'), ('NWFfqOWqLVpObSjhwEfVzBfOrMzgUgfTlBdGHTaHJvYYLhcfMygXDpthBLKjfPXH', 'nrpVawowfMSMrEkbydFddpbAnLVdSgUAEwfXmaOehCdHisSFQlWUjMOtxrqNkBWe'), ('FhrZiQvtxiGCpysSwYFSCnDrGGKArmIsTKgRUAAQTZvTyALqZhbrQWGamKfLcNCN', 'oiuoZiFqTreyumPFkZfofcxYPCJfOQlONGmWdZtVLenwDpaXbtkoRHrILCjfbJbq'), ('yZLjADjBGknyKuhRMXeikXyWUIuZqVagAacmGnqAAOwztQOGrJfdLeiTfzgSDjmJ', 'oDSnHiYRHRiayWQodDbISgsWAMZDRGumJLEKXBswmveiuDqrGxaQZgWiEztcSOjP'), ('VfiVGYhNrteboCzGBUdwonkvMcHIxRmtngiNtjFEaDomwYmRayjHxwwJqcStAkbl', 'eZUEtHVMuZbkhpbmVYNWjzITqlYOXZbyalxjfzMgXZxOSwnxdwmJsNZtDrcxOrhj'), ('NvXCXwjpIxzzKCtLojBAHFnHGMcvODppxYBrMpaEWdLCqpKEVAPdpuKvfbgODnnj', 'yXxSSOZGksywHAcoNENXIFpEkQjZNUOZmCqbnKZRNzQgtNBRyPYsFjEdalBNqUqp'), ('pipDWBOmDnTLCkYCUnVuRJXXdnqpiWEvVjLATzgAindFJHBHjfqjfRKymXbMJEHd', 'zEstGiJWoyTYHLHbMhgnMETpsacJCFDUzMndHSlBkFoDDCmzfAEVwiySKhLoDbAo'), ('eQwdpLGIxjfZHiSktmazHIEZpPeVZlueSMCncIEUBfdZmbAJfZDeaGpeZcGypWZn', 'tlqLadXYoFlOILAmBsZfzhuaoMoXKmVzLyLbeoqvrlCjkLreWQexiFnZxrEVVCIo'), ('VbPlWxPEHSKapYDCLvdLrMWFmmXlZiUIXsJMMDIMvFFzgPBHkzPdrShAihbHHlna', 'TdVwiLQsaRsikSXAAaxGPCWUtKwbGeJiGJVAXtbJEomdhDNPMjDjvZFEiAmvMBIn'), ('eoXuJetSkEjCvgtXyMeIrNmICUsAsNwupMgEdToLKcQlbazQtzNxlUKZmOXJyYpY', 'DdmyiuwjTEbBvjMtYnKcVqOtWczjywbixuSSuhiIaTGOPEXWWWgNZuWbuaUbhAmn'), ('LguJuMnKpYrzKTOhkCCpRlEDQKtMMXBbWpLYtBwejngxbBLYaDiSFcJsNgEQsVMD', 'SfIOGsTthECwkBDxxhcVhnqysPVLLlWnksfggEyVkxVsBkFQLOpPvGazvojCZjfj'), ('wtmgpXcFdYtkIDMsFtULrDehffQYjxPCKelYJLUvEDHguvWNxPAaFPCRbkhilekG', 'FhFhYRYBHoJcqgRxKCZLFBxdLhbMBWBQtTdXKJKPlPrHYxIwICJNfmuwmmytvCtq'), ('rVjGfGEQyByQHSMrXzhppjfBPJsOaQblCCOkNSwjObVvSkYPhMRDvysKKNODHklf', 'zCDzHiSoVrJSKauCVeIDxrMPoVPXadcmxTcQJioDwzWAOhqPVQbegtYEIvZyQyUV'), ('ozECLrjsCmxmQcXeIaojovnLhQJpndmmvqNWrywFSPLzWhDpCAgtreUERECRrEfY', 'nlKbudtQluDkeiGwKkWUkVGQPqyMWyVIqcnyUbYsQSLUjkTAJOGeXbauOjtVBySm'), ('paheWRCTqCvkSStjgPQAwDJfniWhRPcVeNrtruDknAPDGQrGpXkkYsIbQCyuPFRU', 'GWLPzmVNmZlORQgVADtqjnmocPyyelObEmqPqPtbASLScOEpIdVqjFYlnpveygJn'), ('lNTouRmrZrfEIWQPkJakEOmTgLNlsXqLTIthhdsZeYveUDoPikfhQucAXlCDEIig', 'qzeMHdqQNZNXAHrlvNJnPlGinndtEOAhcKtTPOnVPwUbcuYTFEAigFFyDZZGglzf'), ('CfoKagTCiKTDrCONRciIvicEwxDnEblaLQSMjWeFrpXXdaJSaQNdgmZwIGmTWbaK', 'jbgQNSjSshwDAiDWnkQcUTCPMJeIyTkQVvidWrpIMOcGXAtqCDqzhLYMSDcxCUBw'), ('PgEqXvYBxsYtqNnEfybndYkiKuNuogVgqPWqCOhmmJjzBVcnFVKmUsOtWylgpwGN', 'jhzPAaQjJQIfwtFyUVonRCYgvRVuLcaEqDWLcMKfuRvNRKHIfmBiOeFAPNEZQVQD'), ('GbMMfBibOtQHngJigAsUamnZPpnwqEKoWLzslswwyJQuLMibVbRaOWdJMMsNNeyC', 'VFJrtrKYIaXmtUutADZKYaiBkbaZNbCGEHDxChPEKdApYjJYKBvtJbsCywyTWHGh'), ('lhHwXZDsTShUxTZjYyloeNybMzudKuxNtaSfPthyjqtqpUXRbAZoJWoevcCmNHmQ', 'LiWNTaPdcRASLOzfuLQIbgfPXoxctvAPryRYtySRicltIgvZHYSCkySjGfkChBSG'), ('tBsstjNlFeQOMEFKsLmnYHeoFQzeCkDQWwUTnflMHqwhFfiBTJGkZlhMlauiiUUH', 'LrdkyNgwFlBQgnEyGwIakdibjDDDyhbduAzTmbuDyeZRnISJpsmtMXYMdwGTaqTY'), ('cUJoNibWqxAkYicRWmpRFBBZdCZLNtFGmuavqLjhHUCKqieyaXUMMAfmJniXgAGy', 'VKvqguNrZKMvIodGrzPAQsGwahXsXVgMLbIpZorWztEDMZPaTujjGNdibyvXbMuH'), ('GFDoDstSVDYBYijTtDDYIrnEhxGAckPULQFEjYFcKkAXsIBooLTdZvvzMfnKvaoq', 'nEoIcWDjxHcQFcDnlSYLemMvxbZeNkSLFUadhHyKPwyUYguMkWoJjftLwDoNZwCM'), ('UKJMchxwUxsoBpVzRreXzHzSBnTPwzHzAxKaDAoZiZLntfwZxXjGKzsyfBAKGfUn', 'VdYflTMtXQwWrFFLGvVCSYvkTEMENWzlSHjqPFJVSHjpGbFiRQDPAuwFWYIPWgtd'), ('zENSVbqQNOccuTZHhszrXEQnRcpZRVtwhBmHOBUHcoHFywmDeicURhabQLlaMYZv', 'CndYlsNmebmDqZUAsuIWxvnXQFTotdDzHpTRuQUQVrLVRKmJuoJeCRpRPMPtULtc'), ('zbWPYPLBHoCVAsylcsHMVmYxczrWqzajfaXNLmDvsBhJTHlQczVlLUtUaTAfrFCs', 'ycKIYIPuzjRphCKsJtMPNrAseKTJLwDDGHjanjCnJOcxHTyyshBGauLZtoaHyNAs'), ('guAlSYlfiwzvrZHAxDzVWDrlbtuJGUspxgVrydHCwwjQLmGJepErebJnugQuREHo', 'iAjUzAfnMiToGlZxLZDRjGcGfWJRahuRBdZMshcpEBxBInOjrHxeqHNGomDFdRWz'), ('OWeOrZNnluJStzsLwkOXKtwqJVblzzfddpnHwmzirKjqIHhcfvrZvITKuFkbjlKi', 'ImQTUjWVpxLoPuXuwfvhcbUIzbpXqcNueSmNcSkoNyecanzdXVUBYIvtlCBXPWon'), ('TQrMrflOCVsXewQViBywOHxZuEaVFXSwNcFsYYwVZCuqbPFfNEFczcNpKwXClWpT', 'czJVHvkMSSopyISsImpOjCXsZfFCBPdJCFlxfAsrWEmtnmUnrStICzMzxCqsirHL'), ('wfKtfnTfGDpQiHzRBMCRxkNsvkXkYBqmEkhtTfpFVwYIyMnrHOTrEMjVNrXbjhTz', 'fUHWvIswgCSKLFxLUHqksVsFcIZZwkUDhXwBNlvSSPAlxWSdKjBRDOoGtSTfASjg'), ('VdhaSheNDWcrMiMFnUyMbCXYmRqMOYVAemOSoTUiESGYgZwXVDekhOOvxQdixxvp', 'CanqnCkYbujUFjCULgewMdTTxjCBsltshpjzvGOgTBdPgiOjowpPeMeShlNlEwWC'), ('CDlVhWOYWzCzMgUGhLVZAduonAyRkYhmwWBPilQejorngFFlEfxFGkykvmnpRanz', 'XDQHwNwUUahUxqJZuxtgjIFQdEkqxBPsOuoxSIZYFKXrJuAoBVZbqelXesEACclh'), ('ZFyiskEuRpFSBHrJrcDINwczPxkfAUcHSFBNvAsYZIrkeabOdLhzuzTIztLpMatp', 'hxiwhTmdLnNgJypDDrojSMwrraogjLYTsBsDjAdLZJfibGgCNlJZdGvcsTNBwDGR'), ('UOdsABCTqlwyIbumdNeQzQwDpteAUbsVnVItfTMABRYSvVRxDXkEGRhamwvPSBMj', 'ZgrJorykYlPXSmTDJWTlhULnEFOkqAfdzAdvhSstpeWLRZTZYqWcvuCTmHHGbqWQ'), ('YczzYOuQDtMYMAqEFSUuEYIQuRqnrhNDDVjEuhszTrxfwwZspfYbgJgmbUAWBXMr', 'kjfpGLaqQXZRIzyqbCkKCQxeSRoJBtLlRlbzyemjmDNQEUvXRKcZxinVqVQWiOZe'), ('CWcHrQyRYJRgcgpDLdlzQIzDYsRZbGoeZBGmaBCUkAUhnykkAnRIckxcXpVsyPJY', 'KwsLhCPbynOcVvKnoymZAhtnCeibGwOUUCDfwyeOUtmGXmwHtddGkygrpMHFhQmJ'), ('NteCyrjCVdxwrIMvzGkfsUpzfRSaTYlLmqgnCReKWaRxEFdIcdGBFpljLkPwVbOx', 'jkxSZROzpVQicggXqPFIpqUpDzbfGHQDZtONPMEcLhITIXZXGGJVmbpckmZIetTz'), ('tQiUcGzssNgGuFLbSjpzvdZnymrIuQJKMpGfCKlPirYaxNrdMccoTsssdcvHHeRM', 'xoKhYZePINUqZaBIiAOAiASqDzWenWhWGvcKwrWeQIaWzZAthwLLzrfxemnzeDgU'), ('WALTLwICsnXzLDnILVnOeIqBrnDEasUjbBMytrVtQRixMCiuLLbePROAmWRMLYhC', 'ulXsPbBpsEKXhOoMMaVSlJVTNQtkwroEtSDZUyHEmLzZZTOFJCBzWEOwTySCWEzB'), ('FcQbgWLBaQAoWaVqwynuCQSPdWUpaEgEZDVIQijAJTuXZfvnKiCvZPrQKKPNXKCb', 'wyTVHgWWUtSjKMGBJeqzSqLJCEiYJZDOlgDqMdAPVkwLcunyXnYhrZINIBmxKBru'), ('jWRMnVEKdsJdzENcydDJfclGAjaAYGlSRTXPfzERoDWVKGLXjLrwbIyDKWpgSPlu', 'eeoaELuKKGXBRlzmpPaaQAlrDSsnTTIgjcAhCBqBVMSxIGUCUPkqgTtJqyEDUdAS'), ('vUZBOXHLzaGXglFHoLRVVIJeMubXQlsYMkuOdedtDLZRwuelyQZrMtqYQlDgxpFc', 'ZsvFVPjLcmNpoinIRfvadEDEAwQYzHPOjWneOoITNiPYJjeRwMOyjCYzmEqlBWCt'), ('rLHrBBdVcWaZcQmlDjELtEbYMCNNROKcstjKlEGiVgprqbjJUvCsAHlEEehqZCQD', 'yxEebPyToUxuSagTlCUnfFDUiousTlUjgGgKbowTWnKgZhPtOoJkxdUPeKWAkYRu'), ('MYrLACTevqsRpoOYuXzbWVoDjohVHSCQcFiUFgXnbbrBWLuXSBujklYtKHqEDcXt', 'aAUFcjHNrMIkXPwzWnzlsKFTstfubJEGNUNWmHUlMHNAfIQhejkSWiUUjHHwvuoT'), ('MedtwrdGCduWBqnAGyeMJKnBSoEFRVyfXxChsfarqVkvqXkowzXjfkqHyEjCCNXL', 'LUIJYkqFqWGXBXvQgIeZwMwpOzFpJFlnlbblvbbOBXVpFudjEpqQqdLpSiWNaUeS'), ('bhZbapryJrdzrVjjJxMsEomTDcMENyFqRMaWJsZmcHOcEBKvyHvUMmDAUKHDQLZZ', 'LjOnKFalACDTbxgQwvVLdwKRcwSneVhkmyioZcTYcyJxBKyjYwpnxODQstYmQorR'), ('FErBLSuInyHeOtPXrBTSgagZghhFAzoQQfCuQhWPlORSubGhwLlMmpViNZxAUlKu', 'cMuPrIpqGcjWxWEWKcCuzniQrzwHbyEbAGIdBjRAmZnfVpzvTRdndZxsAwrFiPRF'), ('pDzFMURnOcWJmIQLDFZULgIISwnadrACLZvDTZIbPvdoqQwykOMEuMZgfFxvXybz', 'whAfbqEQiYBAzCyTPQHXDvCsgRutoCyLMUcTRKhEAcHeGXbxymIaHLNFzBsFbkwQ'), ('sPQbKfYIOwHuQTOxKOEaipEOYpKrhJbzWzmCVxWLUMTMpxzGcWEHvscVuFlfUaCR', 'wymiiqbmbXndVSzmtTagWkpSUnJYLGrdIcXlzNxZhsuukobxFvxYaEPOzcDLigju'), ('KrvvyIdHCYKmJFnpytoaXgxfSwoldOcMcJlcIkPzXFEiDdHKGJuaXdKLVtxNAjJt', 'ELSQwOOEogwvBWsuvWcnCyTYGcbhLsDBSSjehaIQSiayaoYmjvLdlBxZfiZEzqgB'), ('weSkJpswPnnLfYmrBSgXVgpoRwWnUYjNkemnavirnHHUbCpHuoTrrlBuMiBdAHqQ', 'PKaFMihAUIuzRaWqSxlZlFHDgDdVtSrMYtYxtzEoRjXUyjgAJQawibrDpKDLasVK'), ('ujnkSIBDYSUTgjqpodBjXpKPMFLyUQXjaUVXPgzbCfsSHViRKxIdKiXUyzQRlTtp', 'eyIVvMpcYidrBmfVYxjcIwRsanLhkEbdqFFanKkkDoTMPyEDDvLNSbUSJHQaiGNP'), ('XSKmjsJLFdLSXZlyhEiEiRTMaClaiHwvbRlAZqaLSavEMqTQLuBPlKgdahmhzyLk', 'jiYCxoDEpictkZQRdWBQiBwpwWtueWtMdTTHfhUGVkHTJFcXRCZJmcxHDxOzvUuu'), ('SQHamxOELnDsZoYQYyfqsDrUGiFPTgWmpuPeiZvjxWJuPfuCBaUuNAQhzBBIvXPX', 'gdMkUKEUcZhDPzGlzsaqOCpKdXXDMrlXvaLLqjbeTQAmrAYtQzvSQgczDSbjSBvv'), ('lFzdmRwGDlwndlHFMZeAJiHPieXFEFgnuiPmaBfCBzkXotvmWpmumEzHyuVmAKHy', 'yAVtNsrsEBqYMxMrhzLjaBMCBfjRFbSgIiPRdPzbbMtidEpRKGuVlHYAJJPHIgrK'), ('kUHgiUtcuFvGJqbcviMVUYLPwkWXCBZUaFTLqJfiqSOkbLvgwbYRcnnWVfROwVmG', 'YYhrdhqrUAGvjibweKpIPaiIRaEUUtSrocAxAHFoTsQDUoLBSpvpfNZLXHTbhOtG'), ('dErdYrMLUeNTnNWSVjylcseQnNkkPEDWdPrKgHbpYnMZNMFJMkRYWLXdDWBEICrU', 'erFSnCDYzlOaJkAgXGnLuREOBiaiQToGXMoKeEkXglzahdmfQEtGUaedOwrSnwLv'), ('zdzLCQRHeAEdgPWONbAoyKKSsbMkzQzqASiFPOWyBIxSPdZzRlvbSqXiFKJIqiYq', 'MNlHLzdWjWmrlzvRBfKXCtrJQbaealCECPxEYHQYhJsOTuzqlqboIuEvALHByqpG'), ('xfbqAczwemboLMXmZdpCvmppSOlqdCIrKwIXQHYtyMaqziXGzApFvXkOPMqLEsFL', 'WyvhVrUSUzFrTsxxpCLqNIyntEzVcbLjExEjDvJpXhkuMGRlAlrJkIxRhWYUrCzc'), ('YPBYvCJnJPdUMpuQITKaNtEYATnxcdEAoUGzoyFzrIkaYXxeFZABOybCLbJsGahA', 'TybfWdkaraCfTOgzUGOjutGVQJklUftJLJbySvYkMrpIaOuexiwcOaZWpwtHImNo'), ('HipgibxWJyRgQSyRDEFwQrCcxkHcrfLRVyerdoEjAjQFVQiBfGhIpzFnbnmpBgSk', 'kMMQXkGjikHJqzEeIuQtbvTLNRTKvvkCXUZHYsPrchkSGdRrGQnYoIOuBdIcasLt'), ('ImssdbavdsuNWNZeNGobfrCIlzXhPbLumSZlRuKozjhHQwjeMehJubSmAajGzsHT', 'cAUoVFUevaZmlvQHvdaODjyfiqgrBwNlfKxCcloIgvHfZSayTnIDEeofczEbiyHh'), ('vaZKBFYcQrOctluUdesppIWdSOxMBDarRznZuwwaJZdcVOKiJuqPQqSlrFToyBRm', 'SvgDxowuulpuqxDlDsscwvbfPKonLIkioRLIeqgdHldwKtSgdulGyrHgSIhqpQKU'), ('JVxnpbsqIGomibffbXKhluOzlYksCZfyMTnhTkaeTsqynUTpXqPmUqvMBurXSXuO', 'axTStAyDOvVZBVPgEIbgWPspFNnHPNaxLLbpChXUYzsOzfTqlSYFXvbZTSHxoGvy'), ('xYGZJYTEWWECNQGNLwoNdwJOcohCyOpqwaXozjrVDSvYDrmaGxEseceOUjNVaHHz', 'bNJRbIZxCHJSvhyrMFiVjTMNQkYysLWnYCLdNGGAQEeTYfPOhwMadFJFboIKBdoB'), ('OdHMirTWuAiJcsdczjuHEzbUiTJrbcKjReaUjFltGfunDAiKFTjbNIpMxMLvcqAg', 'DfzZZfZrxNSxnNOKWgdjSZoRGPAmLUWOvKGVtNkGGnTKGBfsFdkoroyerxahaVOl'), ('WtADdsrPVPFxVauSovLscWqzbXSZzTaSvMCATHaGEccjpYzowqNYncihTScLCLZD', 'zRwAYvulvtjwdHvjoWWDtYqiMfuniIdtcPaOEHxngyMAxUTlIbLdjHmFwGEXLhSm'), ('PTaFifpprNiFNFGguxxZFkiyXvEVBWFGcJwlaBwRTTWjEqmlFOgOgsnnENmRXCzT', 'HkCeSnuZzSumhaAFzEzppZUCoebUtRakzgVXrXxMcruMlikquhRwXXOcwpkmLuzk'), ('IdtmZEqWMlkrfQGxYMkZeBJrXJXWrjSeVrbaYojJjoTGhzWotTXrmMeykmmPAGOa', 'nXIwYyrRqpokVVDQcWCLcABWRZAArVyxMXyFRniedwPJzRpiXSPImRbEzuKxlDYf'), ('YRqtcULaRNjnKFuuJrIdHEosJJWUmieObRABLLOPMYeUzdGdPOhHcgZZeuEiCgaO', 'iPMRtfwteGuyebLQtvMwuFFUgCSBSGLRCXMPdJUuMPqLmUfKqhjESYChkXcuRxUc'), ('vcjmJVIVYabvcoUETsSOTUpPMNpvpubrJOiIFFuXMeeQTgzIaCgRpeSRuwSdAJzY', 'wwfIjpeXFrgaCjcjAWPiEHgrrZhvIuQkAmVYFnMRqXSxlpHTgaaRpFzcRsQTBDax'), ('nIWLhIxQqxYdXfcdwrVPjbcRsVSUpcSrSAKiUQSdTUPBmYszzPtkePKKJfQCyHtE', 'hsBFhYrgAIiRsoMOmyBYEmrMGGltetBAtAxdVIgOyKOxAiKhZrhgxMrltpmnkzDk'), ('QDiAYUogZzbfrEaudGSofewqpaRWalhitrnpjimSjojcQXpnjegfSmWOrBOWdenC', 'mgMLrZhhwIxFLsLsjjhkeMJcAkuczlOXKhztbZTQnbVvvmuodeCZsNTsQqqIDVSa'), ('LWypCzdZWkfQqyMyBmcMnFDUxSKQaRhedrKkUdskXBBwLZvIQuzCOwHRppmSiAfU', 'nSdsMAaFdDDUQaHnilOqtIdyDrfeDUcndUWOcwBblNZdJdKzTKrTBlMnzEfFtrQZ'), ('SYLQmoXDoDVGXXizUmeElgJaekXNrHNaSOMvUFCWsIFtGnIucHlWvSTBMbCLwplN', 'vitPzDZIavwmxNNgHWtuIslmVdGzXHdzvahxfFqyUExWBcrkEVsfVAuDWZMYSvBu'), ('eHCheAHzlivWDQUkIglAoSusqdnzlwLEZaDakQsAeMKTWLVxotEVkInGOYbcFhgQ', 'nDOsYTyKzfbPhmlCMhDvlLzYYvWnlFIgPOxgCywnNkjZDuNYpPCDXlJXobgtuczO'), ('qbEkLlCFYusltLJpDGghIVKuirYJKOnpqVckUtIinaqZKfDWGXRPoTCEwbkCbGGP', 'fVGaZWyDHPIbBpRBLxSUkpbtxKeIvhlkYfyOlOJgAwfEasrZPhoKmpaKVELOnYfp'), ('YoGPkPGtipIEKADcFWhLoudBghSTABlqsgyscNjMFfARHjnReSeBZNLXkbkaATgq', 'lEsUpdYVrmETqMSIVBEbCiSOvScbqKHLITbcHxhGtnStyLlpQqoHKTLgKTfMXoqx'), ('RlWMHYfOZTKzpXkOvfYlVzbMSJWuOBStpbnnWQxyqJTyLpAuESSWIvkWnuhmAyXC', 'aUReHWWWicnKBVxADNkEiNSBmMONokRmnJVfeIrLZJyAbvRevtTScRmXqoxcufIF'), ('ddYGGCfOwPUAETdDwrqxlOdoOPrxcQniOtRIVyWVSbVaHqqfTnXkugXyjQDgPBpW', 'kcGKjhgXyKnawaUwyoaueAApgDyRLvjWoUGXigtNmUzksQFGmaDEtErEoqsWruLA'), ('haUQEPAJSpWEtcJfuQZqAzahedhAMPFVvlJeUNVOZYQLrvktswiccDGsCaObejDP', 'dwkajhedlyOkXRWlXOJLhZarqVWuvblgCYTLCvxNsewiTAoOXuJlsxfIPoiKVGjq'), ('LFQcqxEHvLweWJTyJLbLVoiPicMmkMwxDOyFOuBciwyKvMQyWkXjHwBTGEhrrJFO', 'dXeFBDMNTJYDxoHkhOJMWNoppcSBijjQPXyEuljotETfSFWaQaFegTGmrYRNEsrU'), ('JBmvoIXkwujPpAWaOLQnMAvMcYGZjYxoRUjatNLTgaNOiKMhwBzjvANiIuftTQun', 'dwUvoSpoEvqvXBUhbMaUdAmMngYOedHWsOAALmEejIxRgWWebjtBuIbWSHvNfsEM'), ('rQhHOwkLlOBlklMAIqyHDkNYLAOOhHWfWryjlmJlkPfrrhnnagwpGuPFBqvCmGqL', 'QYPogrhTXCZNfAmDYTGQcCasZBfOsWYdbISAWuctITrAGHQvaSFfkRnRfRHVvogn'), ('vJPQHNaGXoQHuvqZeQISmXsfpIUYWhRuLEnuCelgRJSBJMcsWAsNNraFQSbrotrj', 'CdCNnNSASidklQwLXNQpcAUNlXxYDqAJzlCBAMaLNTLildfyLBzdnNAbMziMPGlo'), ('xMhMIvrIpMvAXUssRNUuviLElKolfntGACMXVFgmEqnPmnjivRTUfKusQilVXIoP', 'PTyRLohCrRruzbsyhxwDhggpGmkFGLYisiOJVSPilrDoFdxBaTHajMuaAMrXBPKQ'), ('LylalZmhZTWisCGMFGkwdlZezNAibnFWVSLWaIvIXUcDhSkZGeQRADJGIwUGHsmv', 'haLWbcbrKJYqVlxrQyKYfEmenzirqbmxnhbBgCfnbCkdsPSkaoizlJjIvlqTLbGF'), ('BQhChdeGGmWmmrvObkfuVrHlvwyZqFpIHibaAemrljEDNLpBjJvEvfKwbxhqNwrQ', 'EjOILQbcjrAjypTzKgMoAcdArvIiRjSHvVbuTiDgsAHommumefMTrWFvIWGTwUpT'), ('gktVosycDgfoNEwsNXZNQuYDlfoYzgtJSrNOrXaXiabWLleDsIzbnbdeQmnTGioF', 'IJzliDQMPPveQTWRXaEssASGGIejBzyLceOiKRbDkhlNYKfkBiKinQAIXAdxbnbm'), ('XiJspZhpBTcvodYATIkZWLRGWsUNGnZTtWwjpcQLwxBfmQuIlIPViQzhfSWWAOph', 'OiIJmVocWgELgsKtQDqQHZeThPMxYAWqdYmZJxtUJbnAfpMbztEfznukJDdzoyMc'), ('QNnHyQTafcWhDzcNBjDEbioQujgfqJpBgovhbkgnrvxUBEFKuqZiAiErZqeJbMEd', 'yJHiBgCtARPVeYurVSaNRYVhMkBsCyaRfsmOLGJaFeRkPSHInaYBMJAQYSTVQumf'), ('fFNQquvUKQhvRqjBsGlhDpICtLnePVrVJmBxRGihqGAXIogNYDVDUrIrjZxCuXag', 'MRBftwgQACpaeMIfiRjUrCzNMlJHrTRzMMDCrBXqExrHoYxBGbPkAinLHlfiwZzo'), ('pwqezOYNODNguvFnrcEOkNWUBJRNWTTctDbnSPXptnuXRQMESEiVARFlcGMnYijF', 'cXUUXsusnPHQvSwPrtCEURLfxklXjQcEHUyTajhnhhSovXrPkdouDISjldFJYdaZ'), ('oPZTpnopqcebZLOUPdmMcJJGYLJRGDcalEfBkrJRQZcHJVJAmogsVIJQshNxrVdp', 'IALEOTKDwrbtHjGxGVHKRcscSANETfAPruTUVOHnvoQBWWKWzmzBeZgItpTJaDjh'), ('FbMBytPUEaNoigluAlQzFfQbgfyimwoEJJZqZOxWJmpWzByYQjbvwVHyrObTdYnN', 'GsrqbNkxsCwTmpLiOibWpWfokdFuFZuDqRAZTQYJWGlmFGNwcFeZNDnnDbNNgnkh'), ('zRGIVrKlGXZZfVEbXIiQIIMleknDdMEGcHGnAjAPNfUZwvEdtvQBQabyAPbXsYMp', 'FMwSEdsUhXKMAREGtZsNDogkOFBrNKjPKLlUxeOIpMDyrHaMjkmJSUYJRwetMuRi'), ('iynIKyfJKmLSgQYaPdKrrsaPmhbnzZHKXIbJpHwmrVuzNeTLPpxfDqebNJpxoQAX', 'WjKfTMUYioQTcYCVsZbUjFZhuqsqlXnONDplseZHCYkGvKhQqqYnrVqUGflFJnka'), ('SRxkZbZwBsnwQruYiSxDgPIaqwXkKrIkIJdTTzTEBmPHJntRddvBDjSrgvcTBDCU', 'LzsbZUQCHiFgMcUqZISQPpqiQCRBLzvwUflcXdYevUKZJTmUSrKQMziOoWkqnvJk'), ('ljEIelfRkDKQDoQgXeIpAhHUpocNkYmWzcqMwnluqXxqpCDgqWGNOhjFUdhuKevA', 'YkdjVOBIIREJhbJJDGlESExzYzljKbEgtUwbNeytzjcWpmpQcohyphFDofwaBBpk'), ('zGlYuxAtchJCebjBuRCmRTHCoSnENxfLnZdjoSHQajlYUVulVngxRKnDgygtatMS', 'RZjQRdRdIZKyUbLbyQKgDTkTsWCnYZkFrVDbpmlBQYWAPZMstQIIPyUYFXMhtuUg'), ('QMJSyOCtrnZIYWwQOzwLqoFXTXJCbHTlGzSIjsHZnifEqWNemeNdtbVxCINisWIf', 'BJgkTEqJBfTzLZIMLrLGPQlTavRCcXNxrdLyiMuautbgcfdvltLhOVIJDBEcBFyZ'), ('pbCOsDmbyleclCttYPEedrQMwqDDorJaXpGZhnQwUZzxaIqVNKJZvAFpXYggLJoA', 'iVJCmxQvcfMeXJNEYOCMhhSGEhYpETKgIBMwPZtVMBUsSugUZtAEODlWprptCETe'), ('dgsHivvypfWOIByUZgEoyhdOoxjXNGieoezZqMQUDTgiuSeathANTWLerjJszHTz', 'NJiXPJvcAiLoDUkIFxcKpwtKaEmpwNmyDtYnPgLhsNGlFqSdhFcofvMAtAkrhgwH'), ('mkCCtzdCLjoYOdQjDOfoXOakCHjrBUNKWRWsNwHWbxLfOGpCxprLxWGDJeluPVjC', 'HfYNafhjZPtEUvijprTGosdvZOsynLirnYJjBZygaiNojWxQJwYahhwTmncewIBl'), ('RQDJspajmLwCSdORkKkNDVRToFrosiKHyIQsFUNSbphPXANjzhMfnTkWJCrXxtes', 'VfxBioAUpjCzukfJLyEYfhRoIjlTKLVKakXjyehuZkXHPuIZmjypDGrsaUqDjcos'), ('FHVNcWwQGmTpbtdDEKfunhymkCRGNygFEaYzYIKOlOELTRwaNDrWHYnueulJAuCY', 'MUGQtGVYKcEfRAZxWRFtTZHMFQxsBTpGqOuynpFRllmqIlmYAkvpiwWKoCToZTJJ'), ('AbkriwMrftrrjKQjnfbntstKpbFSXjiuEIsczuphcWNIrdlwdkQgCaoZSqEEvlbA', 'AxcKMZdIGxWvcoSXtlpgEFHqEJogAcNnbGbCSFQXVgOBzgPqFbzxbPMhzDDUcXhb'), ('GWtKZQKXgYRMrKvmKCxFUlXASSksJSOecnaOnnHjAoYeKcQGAPDUqmRyCQuwwrni', 'pQIAyMsemmjQNhCUZbXWPilucaBhenwWZAzcaUOcyiqBGzTDszYdMbHYvuaEgkAE'), ('DdaGEqUjnHCIuTyRofhwUBqcclkkUyRbqDInLRsvyqtEuvNWnLTtZXQoXHhPxqWW', 'GmWQbAqsVUMGrgUsbnDTkTvnxnefwYXgHLdMxMunqnqhyQAuJFvntjtAQyIbKzDj'), ('ogLhmoOwGrnSqBGZVaNCHMWpLLOkofhWcuDeDZgwKQJGkBrMAWtlFJkgdSxyQdUJ', 'WBvbgdzTHoeqtvkFkAEyLcCGZJezoopydlLqkyHnRgZgKenqSgDUXzMTSQTgWhtn'), ('CtqaNJuDIPYONPSiNxDrBKflDAWWHpjzzsIKrZMYNTIwPgioDLzRbvbsbtqVHfoK', 'vlMxipwAhjitCPnSSiUrRZMvpWjBDwhTQCsgnLGryPgjRPPCIPKWHgDmUTumxRZg'), ('fIAzqSkokfZaphXmRnnHRGlqAeLtpugeRVfSIuOnqFUVNNLyBoDRQrzDRPjrcOLb', 'pvcpfiQRCzjanVIkDLPlMNlrADhMNpwtUUMYuoQRuCKXiRbzIXVOKGvvkXapqzIA'), ('wIyBunLdemjzmYXMgePZKoogzcVTwsaNasjEZABFqnpUtQFPPtgGsmmgyccVlLvz', 'cPmOvWERsABXvwWuwhlHxPvSEMrpnGYpLPmLVHfbiXHOvMOjExCLETwrWYYhsuTD'), ('ORBDejqyWDIjjRqzUKxMijonzVYfrWycuPQIsKhzJILvTBVStaFPYctPgxPvKVDO', 'oAfIfASvnKMtuEapvFoqhnNZmGwXbLUcchHGCUxsgvhLahAjzjUMIPNWserZWFku'), ('RRHbBxUBHIgThCpCKOVGkstTOugUbjBCZiRuPEpyKsBOZbbXnHqCsxLxlpLHAPrf', 'ZpjnaTyvqJkfBYsYPSgWebMYBFFicyMOoctPPRncllVinAjrORtjOrahkkguTMdJ'), ('KbKvtdHACWyoKHikGLxFiQvzeqROFIoZqeCVtoIxvNGwKURSILkHWsAKELcyboBo', 'bUagcAWrvHxrsjitfdgldJWsfFTPYqksQExKEudeSPzxRSaCwIbDcCscGQHnCTyi'), ('RDWXEduFTcgoqVHssMnQayoZxtMACWOBTqxGoXuAtDMyihmtoJgSEfPxQTtzVGpD', 'iaWbuvQUalfmeqAUOhtYkwLVkNCwduYdvAyHaxMVyqhSxvHOQlMeUBIbLwXIOaxd'), ('GQXZDHfqnjgRNjwyVAqiWloDpCtWvXMnbGXlSeGJONzSsyHemMLSYXxsOysJqAkC', 'CocCYrMpmZExKIXMkWKOFlXZjIpKpaptlvKJIODCMqreTPjraAPQAigQnTBLbXYd'), ('mvATEUKWFdEHoNrxGDUVCuYaVnMNdShHjfDIvMKXTlYFVOTwfuqKwvmXYGokvCpZ', 'zUnNJWmbirKNuwEInWyTfkLVYyDtZJMxCWcgfQaHXipDiaDvlbYDmHwbPMneMznZ'), ('JPByGAJxGZOtsVFIBTJzXKaKMSVEYeiJSrhQIkAldMZlHRcftTPhluIJDPSnhgLj', 'qespRfEdCTMbnuEwxeXrIHOdaGokHIsLEXdkzoEbLiaBhDluBtihluhQAyXWMgaK'), ('XaIjOUhWvheSBwNoBdRMUQSsLYOEMsaTmDqZrgQBsyfGvWZIREjrKcTeUhMuZhOJ', 'lJOEcjfGJHNpSruvnTutGJvaKHhwREWDSysBWFKxTyUvbyrlcraQNurXLxlhswDk'), ('dBRVWeyOXvwDUjRuDyOVwjjjiHqvfppiCRnORjTNwnwsddyDHlnSElllGTekuOAX', 'fKaNSFMIWvwbgiGqogmfqyhSgQnpByxTTnoLZLRGAYGTreTZMRrTzzMIEwASnNXw'), ('NTSzDyuxZbelxaTurmWvoQKxOSiqcEXRFOThwhGVdqzRWipSHjiaTJzKrDnzCgtH', 'abONsYERVdQwxcylZvmcXnFXdHILIqWxCJSbCXOLjfkgQzaHaQNQrjLGvIGUHlzj'), ('kabHZAJxLElhfxYaEzBhxDOBWOWIsWYPpfkOCCTurUIRrkYcGZsMaVivsttBHkyW', 'HiXSFxmDwfzlfnoVJzfvdkLrfmeVFWpuZaKKtTkaFAjMzHdGVCxUkaSAKpHcTaXM'), ('qikOftvvdeeBOlDEQgJEFDncjsTUGGoQXYnfPxcphQFmEOqWQoXUZXfWODbKrwQa', 'opeVQuOXuuehKXJLTKfteEQJzOSGSDRlXCoUAELkujlOGPqTTaNHnUkjExUzGkIX'), ('RweAcaUyrYMiFJxNYqZjarpywUTosnwCsZJmNwHhlFPfMNNvylEnsoOVUzdWVpYA', 'oQauHbTqtaVlCmEqedqkOPeKwjRXuFIDdlqZbNEwkFxLaOznKrJuqPZYvBCSXuLp'), ('subLJVYNwpnWZTYZnVYqhSVhoVpvknZjSLCWXGSHAhprRahtaFwjzorEjiFYCaqe', 'KGnIhMHAaztgiSEkSFuwvCYeOdInMiiqKsQUFMhggeapXBkcqrCvSEKuEcGFBPOM'), ('iZjzEmimbjoemrVLcwUguPlsyBduNdkrufILPTmRENPgAhfmGwRzVDCAppZuEJfB', 'ztDVESlEXSjIOqfOALsOexXKxtfkKUQfLKOOSMdsoPFzPRacgpJqjlfAykEaPaKM'), ('qUluZcyZRhujRvzlNlzxTZkiTurWZNiQHjZBnsnpQQQqxrjVHmYUGrgwcTgVFtiM', 'XVJLoAOHlCqnYPxriGOcgoEcTrbUScrumGhJIuLWhVCcGbZzUldpItjrefZaMElt'), ('RXHagHZPdVQgGfkPAOWETyAJEVKghDBFcxEtUsIjEggHQZZOirdofMcSEzQFZqrw', 'ZHJqanKCbviEmhSHqkklzrPXCYoaPGivcBsxAnjVJpSIIZdkwnSJNpliFhWbxXzv'), ('QnPNVWDcmRUvAyUsLqLraDTteMyJQrByZBFntmLyKSgkPSAHSUyWemfwXKAHJRdN', 'prNdXQjqBrPRBVLApqEgqMYUsBLrEHHpdfFiGPYWoejYcYWbzqVPFdrXyBsISIAq'), ('xKLVOrCxSfneagfPfJACSxtoWwouRfrpzEgqTGszHxWNRAoSxXZtAPGCcUvPzXuk', 'fqWCQcfPXzSzJLPdyyFXuYDSKcnpuokVZXRWTRMZufFlwPNEGKOoWgHMQtGbkzZB'), ('HuKZfVsyYqlzzaKmEmdDYjTCgkQEwalBLmXpHtBooDWNzhqsbrNzyRWVmxsTDKzC', 'lPdbiGWHchNYaVQkXcFmpnYSmMLHMoZSlstPMrCaVWcGcDgkduQYEuxEbzAwbQwA'), ('jDuATRTJvTovHENQwvKCdNuASJygDnKECongDowlXFzvowWKZVNWGtuqlHbFVkgP', 'HDPecBXslyEtOfQfQCNPgAwgFZkBiesRGxJNReNqSrZpADwUyXWnmWekLdgSupdM'), ('PYmWzoXznbFGJdPqrGjtXQOwSyNEWkkcrubSCrIJdULumWaITRqynnadzvdhqlsA', 'haaciISlisSWSJboTKwgTHzMCEkHrchZeiTrTVKVPCFODvmiyqNqkKpmZJYCwHlF'), ('bguSAwxjTYhcrznaVlHKSASjDNAJPYFpqxQgobASlthiYkdSsoyzPeXspcUETtzO', 'RiXwPUoLzginbttUZoUDfYafokYUmXKRWAGeBnZkyhoiASUurzGhNhstbJrOJuVt'), ('HWwFKoEZJxtmiseOJjajIajWFATRoEJcwZQkgYmoeoplDVfgGZwuHedxdPDqsJxO', 'zJlomPmwCPhTAcAHNWEuDjlyuOpDQzmmJJLQgnhTfstkvxTrkdlrOiOJCgPHDKvU'), ('qmvRtkiufnUDvehiUpUifpjZPMuesmXhdKcSqsknDCWVvzACYtDHgurstrsvTbRU', 'hkbiSFpMhQwXMQsqQnFbSFNaLfgvYhDtduyDwFQRDkhcrdQUyxIadrMlqTMJyJYE'), ('fwrWtQhRBJbQCuErGJmedgNWmvLEBWzXEZYrazQwirRDZYgioEquPNFLyfZjsmOO', 'ZgNKlQOfegsrknNhJCWhQqCoMEOgdiRENKaqPtiQQEOBVFANIymqvIwrKtNArxYz'), ('LBAoWTjAyygvMVXleLkPOvPszvmxaSahnbFYejgsyHQUOuQwaiKrdUvAOZgfCdEv', 'ycijbAsiWfijduRyXRjMURUZsLTAJoAXLvmqeZIStugwqvBqZZypPBTzuRcQtaJb'), ('QjvveUjziANFtufVAFfXLQffqloPBdemjvmUcVslcKrHnwSNsVxDntFuoRKSqrzJ', 'UuyjNlhtAQXBiRmOsEubHrqVPwniEqXihbTlTZMxePWAKsCuQPjVqpeaqYGDutRI'), ('aQLxQBFxEMpLRUgXuzFfUsZlEfqCjhzNlXbTaVVXyOinpaKQGhZduztfwQQWarmp', 'EmZHIMpZjzmlflwroePoGhcjWnHhROdiroYUHLbeFskylWozLNpqwNsKtsAMuxfR'), ('GakBHebXOiwOMxnaxwqffuORvimDkeJgSdizNtNrqVXZBDOEGvQfNesaFTsafGjN', 'JMHsHEEAdQHcFoDoifHiTiwEoLSmpjJNqJHHGqGKAHiEaxltCRpAhTSxuACczYwT'), ('pFQELzFedXHYowScviwckJoccNEvdOUNlVamcchDDvnkOoPeXeBXtgNDPFLgRwUD', 'LclzJqvutnBPINYRejyemwrmhnKhoDhpkJuXlQYUiPrmQCVwZFasSireYrnFRcGp'), ('PjwaVHsNbgafxXXsEQrqYJXjqxqYJOwqFmkmiZCDqzrXEoWkibJVWlGYeejAKZQM', 'sZzWGYmXrAMWmdLrawQZLinLtnpoKhKTcIkADgPdWIHXzNzoCluoSyadZNoPWmre'), ('gDEaCiSeDKVAhKgjiQImbvjJQwsJOqYaAKQnLQQytQKbGDGIojpsTesvoGymmBLK', 'hDmxwDgMknnMtLkzTXtetpvYkRzKCQVpvHVwGpwODaGVYEabGZJceerVgkRzbxxz'), ('RdOAMxSyHOmitWVQfxsHtxohHsJktyokGViFpJhBdersmHJsPvFAEJOhkgphhuDh', 'WKvLHNBhJLgZUhqwywhmPKEGYigTBuDOkBhwWwQkZXveQCFdTSZtXiPOQvqWKYgt'), ('nBzvmyfBsHmBvCYQYaJJsILvfmgoLtFvpIRpzESJpiDYlKBIHguiDXpZpDcovNUC', 'SSmvDbZSurwegBXLmcqIDNFPMLrjxduitrYkFpjzWoxMWjZbkOEdBowrQBxpNsPt'), ('rKWqhEbWDhAEhzAgbyuhBpFkYBsGzSFhQooKSyFdTcDMkycFBdLksFjiIVTxcwpu', 'PDNarxHmNtELYRTpCrjSCUoXACPYOZLbOCGUoBcpJubYeFUGAyMtdMxYRmlUmHCa'), ('BdIHWnhAvrEnNDzodoWDZGFXFuqMycuzmSjqaHOgjKwLWfuzwAzCNGfnUHUrSUTb', 'KbpYKbgNpCGZPQYYyLRGAvAThhrsdukRAvbAeypQmwMKIDdbEwAxliajthGtzJSu'), ('kEDoRRCoFWEXGSDEqJzGUeSZCfahVsMvgBUhhPXxbtYbPupdVrubYeLTIwycguVE', 'bVKiBiuvAmFAATynMeIudGyqBBHrNUoRIoTvLrcufWBfyZfDVoOfKMWqhOlLcDuk'), ('nLKhbPkwIzvXadxTTQlYVsUSEQEVXNPtfjOwrnloZpyIadQdQMLQmdBcaxikoHQL', 'yGkeYefhhadsPLqWUVgjyzFlxQGkjDUejhMeEdwfTQvFtpSbGwuPmDBXoJRxZjuI'), ('StShMFEMYaYtRqwrseCNyTDdYowgITKTygJKoTIjJcdNHquVhlDYvBTBLmBsBJlW', 'ZMBtNABXBVtblCfgeCzcJnBVFgZQgrroxqrtgQGLgahmCdDykjpzCTVIhSfUybpA'), ('JyfrgmHoyqaVygrYWcgSATlaSusIZTExasSmjvgSuUYFYsqMBqSWvPFtfDtFOHHW', 'IgNByrpgImtrhiYSGFrDwOvCUVWBRRtkqauXYrQcXptDvkUeNUoBmdIiLbcNFPqa'), ('CKlWSyuPzvQVkoHjSJIPGkCGngVpxppHbRDCARmduvPvVBCmEwcYdqGtPqQmLjBR', 'HpykYyVCpxsPaOmXTklrPqSHcMzPQbTTnfFLxEpTsyMDdlGDGaJPeuqqjwyLIqAu'), ('WVPQnBVJMJFCIuDpKosbSFhldDUUWurTHvcDPJBCXVDnbmxLViqWfTtKvHbdOZRH', 'uKTKtCQtKunvAqzHycIiDDAqjNdADEwVNufKXFLBHYtBAOjiypmyqITJuGUvHHxN'), ('VmjzLINQaWpbztgawbJacgSUmtUBwIDcsIlEAKZkkCUILrvNJHzfkaPWzAEGUNtN', 'LvCnRbEZdmPWEaEWIKITeHDEXeJxmssupolmVWbenxlTuVszyETkQwhWNxnHbFEX'), ('TplvSPHDFYMmIfYfbJngQHbtkBTpsythCQWgpDKvyWIbFQTOSxzNOwWQGXLMoZeW', 'gJAMdpIMwmxlllKPTaCjDlAjDOOJTPMVGAXRzLhkcznNyQbAkkpeNeuGVekMDKkf'), ('afuoyqrWjnvovwbcVgBBCSIrgVJBvYPfxaCoQWDgHsnkKzbULbtpLwZKiMuhJTgw', 'BPavIlHXRgYHeUKTznPAYHYcYQIxESnGGmpGMxjvWfQQVrsuFYfzcRVvzwSMNwSf'), ('sqpBNLFbPHcukbRItbAMUsVdJbutqBvgHaTLopnvztQRWytrPFsyGNnZqmsgObcz', 'pxwqxBltUnZTqlmhbTeiLQYaKsGqPWFWMXpoRrmdRCscjykZxTMYQQgVruYiYCkP'), ('fdbRprbCIIOZBshvGnhdqiVbJQmRZYDYYPnfxOwgZwKCliZPSFJxfnYyHrVAdBra', 'PjwoqDjCkOqoytNRAjdJIApFhvdIBMwPmSdbMGWzjzxImIjaWAwOqBprcIyoMyGg')]

import time
start = time.time()
for item in items:
    start = time.time()
    apsi_server.add_item(item[0], item[1])
    print(time.time() - start)
    

print("time: ", time.time() - start)
tmp_path = "."
db_file_path = str("apsi.db")
apsi_server.save_db(db_file_path)



apsi_client = LabeledClient(params_string)

print("- * -" * 30)
print("query item: ", _query(apsi_client, apsi_server, ["JRIKrInSyZfcBADbXigLiGnHisxpWrEctHEQzrryFjAHFoPQAjEoxQhTPoYgXIFI"]) )
print("- * -" * 30)

assert _query(apsi_client, apsi_server, ["unknown"]) == {}