# Part of the ROBOID project - http://hamster.school
# Copyright (C) 2016 Kwang-Hyun Park (akaii@kw.ac.kr)
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General
# Public License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330,
# Boston, MA  02111-1307  USA

import cv2 #line:2
import numpy as np #line:3
import mediapipe as mp #line:4
from ._util import Util #line:5
from timeit import default_timer as timer #line:6
_O0O0O0OOO00OO00O0 =(127 ,34 ,139 ,11 ,0 ,37 ,232 ,231 ,120 ,72 ,37 ,39 ,128 ,121 ,47 ,232 ,121 ,128 ,104 ,69 ,67 ,175 ,171 ,148 ,157 ,154 ,155 ,118 ,50 ,101 ,73 ,39 ,40 ,9 ,151 ,108 ,48 ,115 ,131 ,194 ,204 ,211 ,74 ,40 ,185 ,80 ,42 ,183 ,40 ,92 ,186 ,230 ,229 ,118 ,202 ,212 ,214 ,83 ,18 ,17 ,76 ,61 ,146 ,160 ,29 ,30 ,56 ,157 ,173 ,106 ,204 ,194 ,135 ,214 ,192 ,203 ,165 ,98 ,21 ,71 ,68 ,51 ,45 ,4 ,144 ,24 ,23 ,77 ,146 ,91 ,205 ,50 ,187 ,201 ,200 ,18 ,91 ,106 ,182 ,90 ,91 ,181 ,85 ,84 ,17 ,206 ,203 ,36 ,148 ,171 ,140 ,92 ,40 ,39 ,193 ,189 ,244 ,159 ,158 ,28 ,247 ,246 ,161 ,236 ,3 ,196 ,54 ,68 ,104 ,193 ,168 ,8 ,117 ,228 ,31 ,189 ,193 ,55 ,98 ,97 ,99 ,126 ,47 ,100 ,166 ,79 ,218 ,155 ,154 ,26 ,209 ,49 ,131 ,135 ,136 ,150 ,47 ,126 ,217 ,223 ,52 ,53 ,45 ,51 ,134 ,211 ,170 ,140 ,67 ,69 ,108 ,43 ,106 ,91 ,230 ,119 ,120 ,226 ,130 ,247 ,63 ,53 ,52 ,238 ,20 ,242 ,46 ,70 ,156 ,78 ,62 ,96 ,46 ,53 ,63 ,143 ,34 ,227 ,173 ,155 ,133 ,123 ,117 ,111 ,44 ,125 ,19 ,236 ,134 ,51 ,216 ,206 ,205 ,154 ,153 ,22 ,39 ,37 ,167 ,200 ,201 ,208 ,36 ,142 ,100 ,57 ,212 ,202 ,20 ,60 ,99 ,28 ,158 ,157 ,35 ,226 ,113 ,160 ,159 ,27 ,204 ,202 ,210 ,113 ,225 ,46 ,43 ,202 ,204 ,62 ,76 ,77 ,137 ,123 ,116 ,41 ,38 ,72 ,203 ,129 ,142 ,64 ,98 ,240 ,49 ,102 ,64 ,41 ,73 ,74 ,212 ,216 ,207 ,42 ,74 ,184 ,169 ,170 ,211 ,170 ,149 ,176 ,105 ,66 ,69 ,122 ,6 ,168 ,123 ,147 ,187 ,96 ,77 ,90 ,65 ,55 ,107 ,89 ,90 ,180 ,101 ,100 ,120 ,63 ,105 ,104 ,93 ,137 ,227 ,15 ,86 ,85 ,129 ,102 ,49 ,14 ,87 ,86 ,55 ,8 ,9 ,100 ,47 ,121 ,145 ,23 ,22 ,88 ,89 ,179 ,6 ,122 ,196 ,88 ,95 ,96 ,138 ,172 ,136 ,215 ,58 ,172 ,115 ,48 ,219 ,42 ,80 ,81 ,195 ,3 ,51 ,43 ,146 ,61 ,171 ,175 ,199 ,81 ,82 ,38 ,53 ,46 ,225 ,144 ,163 ,110 ,246 ,33 ,7 ,52 ,65 ,66 ,229 ,228 ,117 ,34 ,127 ,234 ,107 ,108 ,69 ,109 ,108 ,151 ,48 ,64 ,235 ,62 ,78 ,191 ,129 ,209 ,126 ,111 ,35 ,143 ,163 ,161 ,246 ,117 ,123 ,50 ,222 ,65 ,52 ,19 ,125 ,141 ,221 ,55 ,65 ,3 ,195 ,197 ,25 ,7 ,33 ,220 ,237 ,44 ,70 ,71 ,139 ,122 ,193 ,245 ,247 ,130 ,33 ,71 ,21 ,162 ,153 ,158 ,159 ,170 ,169 ,150 ,188 ,174 ,196 ,216 ,186 ,92 ,144 ,160 ,161 ,2 ,97 ,167 ,141 ,125 ,241 ,164 ,167 ,37 ,72 ,38 ,12 ,145 ,159 ,160 ,38 ,82 ,13 ,63 ,68 ,71 ,226 ,35 ,111 ,158 ,153 ,154 ,101 ,50 ,205 ,206 ,92 ,165 ,209 ,198 ,217 ,165 ,167 ,97 ,220 ,115 ,218 ,133 ,112 ,243 ,239 ,238 ,241 ,214 ,135 ,169 ,190 ,173 ,133 ,171 ,208 ,32 ,125 ,44 ,237 ,86 ,87 ,178 ,85 ,86 ,179 ,84 ,85 ,180 ,83 ,84 ,181 ,201 ,83 ,182 ,137 ,93 ,132 ,76 ,62 ,183 ,61 ,76 ,184 ,57 ,61 ,185 ,212 ,57 ,186 ,214 ,207 ,187 ,34 ,143 ,156 ,79 ,239 ,237 ,123 ,137 ,177 ,44 ,1 ,4 ,201 ,194 ,32 ,64 ,102 ,129 ,213 ,215 ,138 ,59 ,166 ,219 ,242 ,99 ,97 ,2 ,94 ,141 ,75 ,59 ,235 ,24 ,110 ,228 ,25 ,130 ,226 ,23 ,24 ,229 ,22 ,23 ,230 ,26 ,22 ,231 ,112 ,26 ,232 ,189 ,190 ,243 ,221 ,56 ,190 ,28 ,56 ,221 ,27 ,28 ,222 ,29 ,27 ,223 ,30 ,29 ,224 ,247 ,30 ,225 ,238 ,79 ,20 ,166 ,59 ,75 ,60 ,75 ,240 ,147 ,177 ,215 ,20 ,79 ,166 ,187 ,147 ,213 ,112 ,233 ,244 ,233 ,128 ,245 ,128 ,114 ,188 ,114 ,217 ,174 ,131 ,115 ,220 ,217 ,198 ,236 ,198 ,131 ,134 ,177 ,132 ,58 ,143 ,35 ,124 ,110 ,163 ,7 ,228 ,110 ,25 ,356 ,389 ,368 ,11 ,302 ,267 ,452 ,350 ,349 ,302 ,303 ,269 ,357 ,343 ,277 ,452 ,453 ,357 ,333 ,332 ,297 ,175 ,152 ,377 ,384 ,398 ,382 ,347 ,348 ,330 ,303 ,304 ,270 ,9 ,336 ,337 ,278 ,279 ,360 ,418 ,262 ,431 ,304 ,408 ,409 ,310 ,415 ,407 ,270 ,409 ,410 ,450 ,348 ,347 ,422 ,430 ,434 ,313 ,314 ,17 ,306 ,307 ,375 ,387 ,388 ,260 ,286 ,414 ,398 ,335 ,406 ,418 ,364 ,367 ,416 ,423 ,358 ,327 ,251 ,284 ,298 ,281 ,5 ,4 ,373 ,374 ,253 ,307 ,320 ,321 ,425 ,427 ,411 ,421 ,313 ,18 ,321 ,405 ,406 ,320 ,404 ,405 ,315 ,16 ,17 ,426 ,425 ,266 ,377 ,400 ,369 ,322 ,391 ,269 ,417 ,465 ,464 ,386 ,257 ,258 ,466 ,260 ,388 ,456 ,399 ,419 ,284 ,332 ,333 ,417 ,285 ,8 ,346 ,340 ,261 ,413 ,441 ,285 ,327 ,460 ,328 ,355 ,371 ,329 ,392 ,439 ,438 ,382 ,341 ,256 ,429 ,420 ,360 ,364 ,394 ,379 ,277 ,343 ,437 ,443 ,444 ,283 ,275 ,440 ,363 ,431 ,262 ,369 ,297 ,338 ,337 ,273 ,375 ,321 ,450 ,451 ,349 ,446 ,342 ,467 ,293 ,334 ,282 ,458 ,461 ,462 ,276 ,353 ,383 ,308 ,324 ,325 ,276 ,300 ,293 ,372 ,345 ,447 ,382 ,398 ,362 ,352 ,345 ,340 ,274 ,1 ,19 ,456 ,248 ,281 ,436 ,427 ,425 ,381 ,256 ,252 ,269 ,391 ,393 ,200 ,199 ,428 ,266 ,330 ,329 ,287 ,273 ,422 ,250 ,462 ,328 ,258 ,286 ,384 ,265 ,353 ,342 ,387 ,259 ,257 ,424 ,431 ,430 ,342 ,353 ,276 ,273 ,335 ,424 ,292 ,325 ,307 ,366 ,447 ,345 ,271 ,303 ,302 ,423 ,266 ,371 ,294 ,455 ,460 ,279 ,278 ,294 ,271 ,272 ,304 ,432 ,434 ,427 ,272 ,407 ,408 ,394 ,430 ,431 ,395 ,369 ,400 ,334 ,333 ,299 ,351 ,417 ,168 ,352 ,280 ,411 ,325 ,319 ,320 ,295 ,296 ,336 ,319 ,403 ,404 ,330 ,348 ,349 ,293 ,298 ,333 ,323 ,454 ,447 ,15 ,16 ,315 ,358 ,429 ,279 ,14 ,15 ,316 ,285 ,336 ,9 ,329 ,349 ,350 ,374 ,380 ,252 ,318 ,402 ,403 ,6 ,197 ,419 ,318 ,319 ,325 ,367 ,364 ,365 ,435 ,367 ,397 ,344 ,438 ,439 ,272 ,271 ,311 ,195 ,5 ,281 ,273 ,287 ,291 ,396 ,428 ,199 ,311 ,271 ,268 ,283 ,444 ,445 ,373 ,254 ,339 ,263 ,466 ,249 ,282 ,334 ,296 ,449 ,347 ,346 ,264 ,447 ,454 ,336 ,296 ,299 ,338 ,10 ,151 ,278 ,439 ,455 ,292 ,407 ,415 ,358 ,371 ,355 ,340 ,345 ,372 ,390 ,249 ,466 ,346 ,347 ,280 ,442 ,443 ,282 ,19 ,94 ,370 ,441 ,442 ,295 ,248 ,419 ,197 ,263 ,255 ,359 ,440 ,275 ,274 ,300 ,383 ,368 ,351 ,412 ,465 ,263 ,467 ,466 ,301 ,368 ,389 ,380 ,374 ,386 ,395 ,378 ,379 ,412 ,351 ,419 ,436 ,426 ,322 ,373 ,390 ,388 ,2 ,164 ,393 ,370 ,462 ,461 ,164 ,0 ,267 ,302 ,11 ,12 ,374 ,373 ,387 ,268 ,12 ,13 ,293 ,300 ,301 ,446 ,261 ,340 ,385 ,384 ,381 ,330 ,266 ,425 ,426 ,423 ,391 ,429 ,355 ,437 ,391 ,327 ,326 ,440 ,457 ,438 ,341 ,382 ,362 ,459 ,457 ,461 ,434 ,430 ,394 ,414 ,463 ,362 ,396 ,369 ,262 ,354 ,461 ,457 ,316 ,403 ,402 ,315 ,404 ,403 ,314 ,405 ,404 ,313 ,406 ,405 ,421 ,418 ,406 ,366 ,401 ,361 ,306 ,408 ,407 ,291 ,409 ,408 ,287 ,410 ,409 ,432 ,436 ,410 ,434 ,416 ,411 ,264 ,368 ,383 ,309 ,438 ,457 ,352 ,376 ,401 ,274 ,275 ,4 ,421 ,428 ,262 ,294 ,327 ,358 ,433 ,416 ,367 ,289 ,455 ,439 ,462 ,370 ,326 ,2 ,326 ,370 ,305 ,460 ,455 ,254 ,449 ,448 ,255 ,261 ,446 ,253 ,450 ,449 ,252 ,451 ,450 ,256 ,452 ,451 ,341 ,453 ,452 ,413 ,464 ,463 ,441 ,413 ,414 ,258 ,442 ,441 ,257 ,443 ,442 ,259 ,444 ,443 ,260 ,445 ,444 ,467 ,342 ,445 ,459 ,458 ,250 ,289 ,392 ,290 ,290 ,328 ,460 ,376 ,433 ,435 ,250 ,290 ,392 ,411 ,416 ,433 ,341 ,463 ,464 ,453 ,464 ,465 ,357 ,465 ,412 ,343 ,412 ,399 ,360 ,363 ,440 ,437 ,399 ,456 ,420 ,456 ,363 ,401 ,435 ,288 ,372 ,383 ,353 ,339 ,255 ,249 ,448 ,261 ,255 ,133 ,243 ,190 ,133 ,155 ,112 ,33 ,246 ,247 ,33 ,130 ,25 ,398 ,384 ,286 ,362 ,398 ,414 ,362 ,463 ,341 ,263 ,359 ,467 ,263 ,249 ,255 ,466 ,467 ,260 ,75 ,60 ,166 ,238 ,239 ,79 ,162 ,127 ,139 ,72 ,11 ,37 ,121 ,232 ,120 ,73 ,72 ,39 ,114 ,128 ,47 ,233 ,232 ,128 ,103 ,104 ,67 ,152 ,175 ,148 ,173 ,157 ,155 ,119 ,118 ,101 ,74 ,73 ,40 ,107 ,9 ,108 ,49 ,48 ,131 ,32 ,194 ,211 ,184 ,74 ,185 ,191 ,80 ,183 ,185 ,40 ,186 ,119 ,230 ,118 ,210 ,202 ,214 ,84 ,83 ,17 ,77 ,76 ,146 ,161 ,160 ,30 ,190 ,56 ,173 ,182 ,106 ,194 ,138 ,135 ,192 ,129 ,203 ,98 ,54 ,21 ,68 ,5 ,51 ,4 ,145 ,144 ,23 ,90 ,77 ,91 ,207 ,205 ,187 ,83 ,201 ,18 ,181 ,91 ,182 ,180 ,90 ,181 ,16 ,85 ,17 ,205 ,206 ,36 ,176 ,148 ,140 ,165 ,92 ,39 ,245 ,193 ,244 ,27 ,159 ,28 ,30 ,247 ,161 ,174 ,236 ,196 ,103 ,54 ,104 ,55 ,193 ,8 ,111 ,117 ,31 ,221 ,189 ,55 ,240 ,98 ,99 ,142 ,126 ,100 ,219 ,166 ,218 ,112 ,155 ,26 ,198 ,209 ,131 ,169 ,135 ,150 ,114 ,47 ,217 ,224 ,223 ,53 ,220 ,45 ,134 ,32 ,211 ,140 ,109 ,67 ,108 ,146 ,43 ,91 ,231 ,230 ,120 ,113 ,226 ,247 ,105 ,63 ,52 ,241 ,238 ,242 ,124 ,46 ,156 ,95 ,78 ,96 ,70 ,46 ,63 ,116 ,143 ,227 ,116 ,123 ,111 ,1 ,44 ,19 ,3 ,236 ,51 ,207 ,216 ,205 ,26 ,154 ,22 ,165 ,39 ,167 ,199 ,200 ,208 ,101 ,36 ,100 ,43 ,57 ,202 ,242 ,20 ,99 ,56 ,28 ,157 ,124 ,35 ,113 ,29 ,160 ,27 ,211 ,204 ,210 ,124 ,113 ,46 ,106 ,43 ,204 ,96 ,62 ,77 ,227 ,137 ,116 ,73 ,41 ,72 ,36 ,203 ,142 ,235 ,64 ,240 ,48 ,49 ,64 ,42 ,41 ,74 ,214 ,212 ,207 ,183 ,42 ,184 ,210 ,169 ,211 ,140 ,170 ,176 ,104 ,105 ,69 ,193 ,122 ,168 ,50 ,123 ,187 ,89 ,96 ,90 ,66 ,65 ,107 ,179 ,89 ,180 ,119 ,101 ,120 ,68 ,63 ,104 ,234 ,93 ,227 ,16 ,15 ,85 ,209 ,129 ,49 ,15 ,14 ,86 ,107 ,55 ,9 ,120 ,100 ,121 ,153 ,145 ,22 ,178 ,88 ,179 ,197 ,6 ,196 ,89 ,88 ,96 ,135 ,138 ,136 ,138 ,215 ,172 ,218 ,115 ,219 ,41 ,42 ,81 ,5 ,195 ,51 ,57 ,43 ,61 ,208 ,171 ,199 ,41 ,81 ,38 ,224 ,53 ,225 ,24 ,144 ,110 ,105 ,52 ,66 ,118 ,229 ,117 ,227 ,34 ,234 ,66 ,107 ,69 ,10 ,109 ,151 ,219 ,48 ,235 ,183 ,62 ,191 ,142 ,129 ,126 ,116 ,111 ,143 ,7 ,163 ,246 ,118 ,117 ,50 ,223 ,222 ,52 ,94 ,19 ,141 ,222 ,221 ,65 ,196 ,3 ,197 ,45 ,220 ,44 ,156 ,70 ,139 ,188 ,122 ,245 ,139 ,71 ,162 ,145 ,153 ,159 ,149 ,170 ,150 ,122 ,188 ,196 ,206 ,216 ,92 ,163 ,144 ,161 ,164 ,2 ,167 ,242 ,141 ,241 ,0 ,164 ,37 ,11 ,72 ,12 ,144 ,145 ,160 ,12 ,38 ,13 ,70 ,63 ,71 ,31 ,226 ,111 ,157 ,158 ,154 ,36 ,101 ,205 ,203 ,206 ,165 ,126 ,209 ,217 ,98 ,165 ,97 ,237 ,220 ,218 ,237 ,239 ,241 ,210 ,214 ,169 ,140 ,171 ,32 ,241 ,125 ,237 ,179 ,86 ,178 ,180 ,85 ,179 ,181 ,84 ,180 ,182 ,83 ,181 ,194 ,201 ,182 ,177 ,137 ,132 ,184 ,76 ,183 ,185 ,61 ,184 ,186 ,57 ,185 ,216 ,212 ,186 ,192 ,214 ,187 ,139 ,34 ,156 ,218 ,79 ,237 ,147 ,123 ,177 ,45 ,44 ,4 ,208 ,201 ,32 ,98 ,64 ,129 ,192 ,213 ,138 ,235 ,59 ,219 ,141 ,242 ,97 ,97 ,2 ,141 ,240 ,75 ,235 ,229 ,24 ,228 ,31 ,25 ,226 ,230 ,23 ,229 ,231 ,22 ,230 ,232 ,26 ,231 ,233 ,112 ,232 ,244 ,189 ,243 ,189 ,221 ,190 ,222 ,28 ,221 ,223 ,27 ,222 ,224 ,29 ,223 ,225 ,30 ,224 ,113 ,247 ,225 ,99 ,60 ,240 ,213 ,147 ,215 ,60 ,20 ,166 ,192 ,187 ,213 ,243 ,112 ,244 ,244 ,233 ,245 ,245 ,128 ,188 ,188 ,114 ,174 ,134 ,131 ,220 ,174 ,217 ,236 ,236 ,198 ,134 ,215 ,177 ,58 ,156 ,143 ,124 ,25 ,110 ,7 ,31 ,228 ,25 ,264 ,356 ,368 ,0 ,11 ,267 ,451 ,452 ,349 ,267 ,302 ,269 ,350 ,357 ,277 ,350 ,452 ,357 ,299 ,333 ,297 ,396 ,175 ,377 ,381 ,384 ,382 ,280 ,347 ,330 ,269 ,303 ,270 ,151 ,9 ,337 ,344 ,278 ,360 ,424 ,418 ,431 ,270 ,304 ,409 ,272 ,310 ,407 ,322 ,270 ,410 ,449 ,450 ,347 ,432 ,422 ,434 ,18 ,313 ,17 ,291 ,306 ,375 ,259 ,387 ,260 ,424 ,335 ,418 ,434 ,364 ,416 ,391 ,423 ,327 ,301 ,251 ,298 ,275 ,281 ,4 ,254 ,373 ,253 ,375 ,307 ,321 ,280 ,425 ,411 ,200 ,421 ,18 ,335 ,321 ,406 ,321 ,320 ,405 ,314 ,315 ,17 ,423 ,426 ,266 ,396 ,377 ,369 ,270 ,322 ,269 ,413 ,417 ,464 ,385 ,386 ,258 ,248 ,456 ,419 ,298 ,284 ,333 ,168 ,417 ,8 ,448 ,346 ,261 ,417 ,413 ,285 ,326 ,327 ,328 ,277 ,355 ,329 ,309 ,392 ,438 ,381 ,382 ,256 ,279 ,429 ,360 ,365 ,364 ,379 ,355 ,277 ,437 ,282 ,443 ,283 ,281 ,275 ,363 ,395 ,431 ,369 ,299 ,297 ,337 ,335 ,273 ,321 ,348 ,450 ,349 ,359 ,446 ,467 ,283 ,293 ,282 ,250 ,458 ,462 ,300 ,276 ,383 ,292 ,308 ,325 ,283 ,276 ,293 ,264 ,372 ,447 ,346 ,352 ,340 ,354 ,274 ,19 ,363 ,456 ,281 ,426 ,436 ,425 ,380 ,381 ,252 ,267 ,269 ,393 ,421 ,200 ,428 ,371 ,266 ,329 ,432 ,287 ,422 ,290 ,250 ,328 ,385 ,258 ,384 ,446 ,265 ,342 ,386 ,387 ,257 ,422 ,424 ,430 ,445 ,342 ,276 ,422 ,273 ,424 ,306 ,292 ,307 ,352 ,366 ,345 ,268 ,271 ,302 ,358 ,423 ,371 ,327 ,294 ,460 ,331 ,279 ,294 ,303 ,271 ,304 ,436 ,432 ,427 ,304 ,272 ,408 ,395 ,394 ,431 ,378 ,395 ,400 ,296 ,334 ,299 ,6 ,351 ,168 ,376 ,352 ,411 ,307 ,325 ,320 ,285 ,295 ,336 ,320 ,319 ,404 ,329 ,330 ,349 ,334 ,293 ,333 ,366 ,323 ,447 ,316 ,15 ,315 ,331 ,358 ,279 ,317 ,14 ,316 ,8 ,285 ,9 ,277 ,329 ,350 ,253 ,374 ,252 ,319 ,318 ,403 ,351 ,6 ,419 ,324 ,318 ,325 ,397 ,367 ,365 ,288 ,435 ,397 ,278 ,344 ,439 ,310 ,272 ,311 ,248 ,195 ,281 ,375 ,273 ,291 ,175 ,396 ,199 ,312 ,311 ,268 ,276 ,283 ,445 ,390 ,373 ,339 ,295 ,282 ,296 ,448 ,449 ,346 ,356 ,264 ,454 ,337 ,336 ,299 ,337 ,338 ,151 ,294 ,278 ,455 ,308 ,292 ,415 ,429 ,358 ,355 ,265 ,340 ,372 ,388 ,390 ,466 ,352 ,346 ,280 ,295 ,442 ,282 ,354 ,19 ,370 ,285 ,441 ,295 ,195 ,248 ,197 ,457 ,440 ,274 ,301 ,300 ,368 ,417 ,351 ,465 ,251 ,301 ,389 ,385 ,380 ,386 ,394 ,395 ,379 ,399 ,412 ,419 ,410 ,436 ,322 ,387 ,373 ,388 ,326 ,2 ,393 ,354 ,370 ,461 ,393 ,164 ,267 ,268 ,302 ,12 ,386 ,374 ,387 ,312 ,268 ,13 ,298 ,293 ,301 ,265 ,446 ,340 ,380 ,385 ,381 ,280 ,330 ,425 ,322 ,426 ,391 ,420 ,429 ,437 ,393 ,391 ,326 ,344 ,440 ,438 ,458 ,459 ,461 ,364 ,434 ,394 ,428 ,396 ,262 ,274 ,354 ,457 ,317 ,316 ,402 ,316 ,315 ,403 ,315 ,314 ,404 ,314 ,313 ,405 ,313 ,421 ,406 ,323 ,366 ,361 ,292 ,306 ,407 ,306 ,291 ,408 ,291 ,287 ,409 ,287 ,432 ,410 ,427 ,434 ,411 ,372 ,264 ,383 ,459 ,309 ,457 ,366 ,352 ,401 ,1 ,274 ,4 ,418 ,421 ,262 ,331 ,294 ,358 ,435 ,433 ,367 ,392 ,289 ,439 ,328 ,462 ,326 ,94 ,2 ,370 ,289 ,305 ,455 ,339 ,254 ,448 ,359 ,255 ,446 ,254 ,253 ,449 ,253 ,252 ,450 ,252 ,256 ,451 ,256 ,341 ,452 ,414 ,413 ,463 ,286 ,441 ,414 ,286 ,258 ,441 ,258 ,257 ,442 ,257 ,259 ,443 ,259 ,260 ,444 ,260 ,467 ,445 ,309 ,459 ,250 ,305 ,289 ,290 ,305 ,290 ,460 ,401 ,376 ,435 ,309 ,250 ,392 ,376 ,411 ,433 ,453 ,341 ,464 ,357 ,453 ,465 ,343 ,357 ,412 ,437 ,343 ,399 ,344 ,360 ,440 ,420 ,437 ,456 ,360 ,420 ,363 ,361 ,401 ,288 ,265 ,372 ,353 ,390 ,339 ,249 ,339 ,448 ,255 )#line:177
_OO0O00000OO0O000O =(10 ,338 ,297 ,332 ,284 ,251 ,389 ,356 ,454 ,323 ,361 ,288 ,397 ,365 ,379 ,378 ,400 ,377 ,152 ,148 ,176 ,149 ,150 ,136 ,172 ,58 ,132 ,93 ,234 ,127 ,162 ,21 ,54 ,103 ,67 ,109 )#line:181
_O00O0O0O00O0O000O =(33 ,7 ,163 ,144 ,145 ,153 ,154 ,155 ,133 ,173 ,157 ,158 ,159 ,160 ,161 ,246 )#line:182
_OOO0O00O000OO00OO =(70 ,63 ,105 ,66 ,107 )#line:183
_O00O0OO0OOO0OOOO0 =(46 ,53 ,52 ,65 ,55 )#line:184
_OO00O0O0OOOO00OO0 =(263 ,249 ,390 ,373 ,374 ,380 ,381 ,382 ,362 ,398 ,384 ,385 ,386 ,387 ,388 ,466 )#line:185
_OO0OOO0OOO00OO000 =(300 ,293 ,334 ,296 ,336 )#line:186
_O0OOOOO00O0000O0O =(276 ,283 ,282 ,295 ,285 )#line:187
_O0O0OOOO0OO00OO0O =(61 ,185 ,40 ,39 ,37 ,0 ,267 ,269 ,270 ,409 ,291 ,375 ,321 ,405 ,314 ,17 ,84 ,181 ,91 ,146 )#line:188
_O00OO00O000OO0O00 =(78 ,191 ,80 ,81 ,82 ,13 ,312 ,311 ,310 ,415 ,308 ,324 ,318 ,402 ,317 ,14 ,87 ,178 ,88 ,95 )#line:189
_OOO000000000OO000 ={'left eye':[14 ,15 ,66 ,67 ,266 ,267 ,288 ,289 ,290 ,291 ,306 ,307 ,308 ,309 ,310 ,311 ,314 ,315 ,316 ,317 ,318 ,319 ,320 ,321 ,322 ,323 ,326 ,327 ,346 ,347 ,492 ,493 ],'right eye':[498 ,499 ,526 ,527 ,724 ,725 ,746 ,747 ,748 ,749 ,760 ,761 ,762 ,763 ,764 ,765 ,768 ,769 ,770 ,771 ,772 ,773 ,774 ,775 ,776 ,777 ,780 ,781 ,796 ,797 ,932 ,933 ],'left eyebrow':[92 ,93 ,104 ,105 ,106 ,107 ,110 ,111 ,126 ,127 ,130 ,131 ,132 ,133 ,140 ,141 ,210 ,211 ,214 ,215 ],'right eyebrow':[552 ,553 ,564 ,565 ,566 ,567 ,570 ,571 ,586 ,587 ,590 ,591 ,592 ,593 ,600 ,601 ,668 ,669 ,672 ,673 ],'left cheek':[72 ,73 ,100 ,101 ,202 ,203 ,232 ,233 ,234 ,235 ,236 ,237 ,246 ,247 ,274 ,275 ,294 ,295 ,354 ,355 ,374 ,375 ,384 ,385 ,410 ,411 ,412 ,413 ,414 ,415 ,426 ,427 ,428 ,429 ,432 ,433 ,454 ,455 ],'right cheek':[532 ,533 ,560 ,561 ,660 ,661 ,690 ,691 ,692 ,693 ,694 ,695 ,704 ,705 ,732 ,733 ,752 ,753 ,802 ,803 ,822 ,823 ,832 ,833 ,850 ,851 ,852 ,853 ,854 ,855 ,866 ,867 ,868 ,869 ,872 ,873 ,894 ,895 ],'forehead':[18 ,19 ,20 ,21 ,42 ,43 ,108 ,109 ,134 ,135 ,136 ,137 ,138 ,139 ,142 ,143 ,206 ,207 ,208 ,209 ,216 ,217 ,218 ,219 ,302 ,303 ,502 ,503 ,568 ,569 ,594 ,595 ,596 ,597 ,598 ,599 ,602 ,603 ,664 ,665 ,666 ,667 ,674 ,675 ,676 ,677 ],'nose':[2 ,3 ,4 ,5 ,12 ,13 ,98 ,99 ,128 ,129 ,194 ,195 ,258 ,259 ,392 ,393 ,396 ,397 ,472 ,473 ,480 ,481 ,558 ,559 ,588 ,589 ,652 ,653 ,716 ,717 ,838 ,839 ,840 ,841 ,912 ,913 ,920 ,921 ],'mouth':[0 ,1 ,26 ,27 ,28 ,29 ,34 ,35 ,74 ,75 ,78 ,79 ,80 ,81 ,122 ,123 ,156 ,157 ,160 ,161 ,162 ,163 ,164 ,165 ,168 ,169 ,174 ,175 ,176 ,177 ,182 ,183 ,190 ,191 ,292 ,293 ,356 ,357 ,362 ,363 ,370 ,371 ,382 ,383 ,534 ,535 ,538 ,539 ,540 ,541 ,582 ,583 ,616 ,617 ,620 ,621 ,622 ,623 ,624 ,625 ,628 ,629 ,634 ,635 ,636 ,637 ,642 ,643 ,648 ,649 ,750 ,751 ,804 ,805 ,810 ,811 ,818 ,819 ,830 ,831 ],'others':[3 ,4 ,5 ,8 ,11 ,12 ,15 ,16 ,18 ,19 ,20 ,22 ,23 ,24 ,25 ,26 ,27 ,28 ,29 ,30 ,31 ,32 ,34 ,35 ,38 ,41 ,42 ,43 ,44 ,45 ,47 ,48 ,51 ,56 ,57 ,58 ,59 ,60 ,62 ,72 ,73 ,74 ,75 ,76 ,77 ,79 ,83 ,85 ,86 ,89 ,90 ,92 ,93 ,94 ,96 ,98 ,99 ,100 ,102 ,106 ,110 ,111 ,112 ,113 ,114 ,115 ,119 ,120 ,121 ,122 ,124 ,125 ,126 ,127 ,128 ,130 ,131 ,132 ,134 ,135 ,136 ,138 ,139 ,140 ,141 ,142 ,143 ,148 ,149 ,150 ,152 ,156 ,162 ,164 ,165 ,166 ,167 ,168 ,169 ,170 ,171 ,172 ,174 ,175 ,176 ,179 ,180 ,182 ,183 ,184 ,186 ,188 ,189 ,190 ,193 ,194 ,195 ,197 ,199 ,200 ,201 ,202 ,203 ,204 ,208 ,209 ,210 ,211 ,212 ,215 ,217 ,218 ,219 ,220 ,221 ,222 ,223 ,224 ,225 ,226 ,228 ,229 ,230 ,231 ,232 ,233 ,234 ,235 ,237 ,238 ,239 ,241 ,242 ,243 ,244 ,245 ,247 ,248 ,250 ,252 ,253 ,254 ,255 ,256 ,257 ,258 ,259 ,260 ,261 ,262 ,264 ,265 ,268 ,271 ,272 ,273 ,274 ,275 ,277 ,278 ,281 ,286 ,287 ,288 ,289 ,290 ,292 ,302 ,303 ,304 ,305 ,306 ,307 ,309 ,313 ,315 ,316 ,319 ,320 ,322 ,323 ,325 ,327 ,328 ,329 ,331 ,335 ,339 ,340 ,341 ,342 ,343 ,344 ,348 ,349 ,350 ,351 ,353 ,354 ,355 ,356 ,357 ,359 ,360 ,361 ,363 ,364 ,365 ,367 ,368 ,369 ,370 ,371 ,372 ,377 ,378 ,379 ,383 ,389 ,391 ,392 ,393 ,394 ,395 ,396 ,397 ,399 ,400 ,403 ,404 ,406 ,407 ,408 ,410 ,412 ,413 ,414 ,417 ,418 ,421 ,422 ,423 ,424 ,428 ,429 ,430 ,431 ,432 ,435 ,437 ,438 ,439 ,440 ,441 ,442 ,443 ,444 ,445 ,446 ,448 ,449 ,450 ,451 ,452 ,453 ,454 ,455 ,457 ,458 ,459 ,461 ,462 ,463 ,464 ,465 ,467 ]}#line:201
class FaceMesh :#line:204
    def __init__ (OOO0000OOO000O0OO ):#line:205
        OOO0000OOO000O0OO ._loaded =False #line:206
        OOO0000OOO000O0OO ._clear ()#line:207
    def _clear (OOO0O0000OO0O0000 ):#line:209
        OOO0O0000OO0O0000 ._points ={}#line:210
        OOO0O0000OO0O0000 ._boxes ={}#line:211
        OOO0O0000OO0O0000 ._widths ={}#line:212
        OOO0O0000OO0O0000 ._heights ={}#line:213
        OOO0O0000OO0O0000 ._areas ={}#line:214
        OOO0O0000OO0O0000 ._landmarks =None #line:215
        OOO0O0000OO0O0000 ._drawings =None #line:216
    def load_model (O0000O0O000OO0OO0 ,threshold =0.5 ):#line:218
        try :#line:219
            O0000O0O000OO0OO0 ._mesh =mp .solutions .face_mesh .FaceMesh (max_num_faces =1 ,min_detection_confidence =threshold ,min_tracking_confidence =0.5 )#line:220
            O0000O0O000OO0OO0 ._loaded =True #line:221
            return True #line:222
        except :#line:223
            return False #line:224
    def _calc_xyz (O0OO0O000000OO000 ,OO00O0OO00O0OO000 ,O00OO000OO000OO00 ,indices =None ):#line:226
        if indices is None :#line:227
            O0OO0O000000OO000 ._points [OO00O0OO00O0OO000 ]=np .around (np .mean (O00OO000OO000OO00 ,axis =0 )).astype (np .int32 )#line:228
        else :#line:229
            O0OO0O000000OO000 ._points [OO00O0OO00O0OO000 ]=np .around (np .mean ([O00OO000OO000OO00 [O0OOOOOOO0O0OO0O0 ]for O0OOOOOOO0O0OO0O0 in indices ],axis =0 )).astype (np .int32 )#line:230
    def _calc_box (OOOO0OOOO00OOO000 ,O00O00OOO00O0OO0O ,O000000OOOOOOO00O ,indices =None ):#line:232
        if indices is None :#line:233
            OOO0OO0O000O0O0O0 =np .min (O000000OOOOOOO00O ,axis =0 )#line:234
            O0O00OO000O0OOOO0 =np .max (O000000OOOOOOO00O ,axis =0 )#line:235
        else :#line:236
            O0O0O0O0000OOOO0O =[O000000OOOOOOO00O [O0O00O00OOOOOOO0O ]for O0O00O00OOOOOOO0O in indices ]#line:237
            OOO0OO0O000O0O0O0 =np .min (O0O0O0O0000OOOO0O ,axis =0 )#line:238
            O0O00OO000O0OOOO0 =np .max (O0O0O0O0000OOOO0O ,axis =0 )#line:239
        OOOO0OOOO00OOO000 ._boxes [O00O00OOO00O0OO0O ]=[OOO0OO0O000O0O0O0 [0 ],OOO0OO0O000O0O0O0 [1 ],O0O00OO000O0OOOO0 [0 ],O0O00OO000O0OOOO0 [1 ]]#line:240
        OOOO0O0O00O00OO00 =abs (O0O00OO000O0OOOO0 [0 ]-OOO0OO0O000O0O0O0 [0 ])#line:241
        O0OO0OO00OO0O00OO =abs (O0O00OO000O0OOOO0 [1 ]-OOO0OO0O000O0O0O0 [1 ])#line:242
        OOOO0OOOO00OOO000 ._widths [O00O00OOO00O0OO0O ]=OOOO0O0O00O00OO00 #line:243
        OOOO0OOOO00OOO000 ._heights [O00O00OOO00O0OO0O ]=O0OO0OO00OO0O00OO #line:244
        OOOO0OOOO00OOO000 ._areas [O00O00OOO00O0OO0O ]=OOOO0O0O00O00OO00 *O0OO0OO00OO0O00OO #line:245
    def detect (OOOOOO0OOOO0O0000 ,O000O0OO0OOOO00O0 ):#line:247
        if O000O0OO0OOOO00O0 is not None and OOOOOO0OOOO0O0000 ._loaded :#line:248
            O000O0OO0OOOO00O0 =cv2 .cvtColor (O000O0OO0OOOO00O0 ,cv2 .COLOR_BGR2RGB )#line:249
            O000O0OO0OOOO00O0 .flags .writeable =False #line:250
            O0OO0O00OO0O0OOO0 =OOOOOO0OOOO0O0000 ._mesh .process (O000O0OO0OOOO00O0 )#line:251
            if O0OO0O00OO0O0OOO0 and O0OO0O00OO0O0OOO0 .multi_face_landmarks and len (O0OO0O00OO0O0OOO0 .multi_face_landmarks )>0 :#line:252
                OOO0000000000O00O =O0OO0O00OO0O0OOO0 .multi_face_landmarks [0 ]#line:253
                if len (OOO0000000000O00O .landmark )==468 :#line:254
                    OO0O0OOO000OOOOO0 =O000O0OO0OOOO00O0 .shape [1 ]#line:255
                    O00OOO0000O00OOO0 =O000O0OO0OOOO00O0 .shape [0 ]#line:256
                    O0O00OOO00000OOO0 =[O00OO0OOOO0O00O0O .x for O00OO0OOOO0O00O0O in OOO0000000000O00O .landmark ]#line:257
                    O0O000OO0000O00O0 =[O000000O0OOO00O0O .y for O000000O0OOO00O0O in OOO0000000000O00O .landmark ]#line:258
                    O0O00O0O000O0O000 =[OO00000O000OO0O0O .z for OO00000O000OO0O0O in OOO0000000000O00O .landmark ]#line:259
                    OO000000O0000OO0O =np .transpose (np .stack ((O0O00OOO00000OOO0 ,O0O000OO0000O00O0 ,O0O00O0O000O0O000 )))*(OO0O0OOO000OOOOO0 ,O00OOO0000O00OOO0 ,OO0O0OOO000OOOOO0 )#line:260
                    OO000000O0000OO0O =OO000000O0000OO0O .astype (np .int32 )#line:261
                    OOOOOO0OOOO0O0000 ._landmarks =OO000000O0000OO0O #line:262
                    OOOOOO0OOOO0O0000 ._calc_box ('face',OO000000O0000OO0O )#line:263
                    OOOOOO0OOOO0O0000 ._calc_box ('left eye',OO000000O0000OO0O ,_O00O0O0O00O0O000O )#line:264
                    OOOOOO0OOOO0O0000 ._calc_box ('right eye',OO000000O0000OO0O ,_OO00O0O0OOOO00OO0 )#line:265
                    OOOOOO0OOOO0O0000 ._calc_box ('mouth',OO000000O0000OO0O ,_O0O0OOOO0OO00OO0O )#line:266
                    OOOOOO0OOOO0O0000 ._calc_xyz ('face',OO000000O0000OO0O )#line:267
                    OOOOOO0OOOO0O0000 ._calc_xyz ('left eye',OO000000O0000OO0O ,_O00O0O0O00O0O000O )#line:268
                    OOOOOO0OOOO0O0000 ._calc_xyz ('right eye',OO000000O0000OO0O ,_OO00O0O0OOOO00OO0 )#line:269
                    OOOOOO0OOOO0O0000 ._calc_xyz ('mouth',OO000000O0000OO0O ,_O0O0OOOO0OO00OO0O )#line:270
                    OOOO0OOOOO00O0000 =OOOOOO0OOOO0O0000 ._points #line:271
                    OOOO0OOOOO00O0000 ['nose']=OO000000O0000OO0O [1 ]#line:272
                    OOOO0OOOOO00O0000 ['lip left']=OO000000O0000OO0O [61 ]#line:273
                    OOOO0OOOOO00O0000 ['lip right']=OO000000O0000OO0O [291 ]#line:274
                    OOOO0OOOOO00O0000 ['lip top']=OO000000O0000OO0O [0 ]#line:275
                    OOOO0OOOOO00O0000 ['lip bottom']=OO000000O0000OO0O [17 ]#line:276
                    OOOOOO0OOOO0O0000 ._drawings =OO000000O0000OO0O [:,:2 ]#line:277
                    return True #line:278
        OOOOOO0OOOO0O0000 ._clear ()#line:279
        return False #line:280
    def draw_result (OO0O00O000OO00000 ,O0OO0O0OOOO000O00 ,clone =False ):#line:282
        if O0OO0O0OOOO000O00 is not None and OO0O00O000OO00000 ._drawings is not None and OO0O00O000OO00000 ._drawings .size >0 :#line:283
            if clone :#line:284
                O0OO0O0OOOO000O00 =O0OO0O0OOOO000O00 .copy ()#line:285
            OOOOO0OOO0OO0O0OO =OO0O00O000OO00000 ._drawings #line:286
            OOO0OOO000OO0OOOO =np .array ([[OOOOO0OOO0OO0O0OO [_O0O0O0OOO00OO00O0 [OO0OO00O0000O00O0 *3 ]],OOOOO0OOO0OO0O0OO [_O0O0O0OOO00OO00O0 [OO0OO00O0000O00O0 *3 +1 ]],OOOOO0OOO0OO0O0OO [_O0O0O0OOO00OO00O0 [OO0OO00O0000O00O0 *3 +2 ]]]for OO0OO00O0000O00O0 in range (len (_O0O0O0OOO00OO00O0 )//3 )],np .int32 )#line:293
            cv2 .polylines (O0OO0O0OOOO000O00 ,OOO0OOO000OO0OOOO ,True ,(192 ,192 ,192 ),1 )#line:294
            OOO0OOO000OO0OOOO =np .array ([OOOOO0OOO0OO0O0OO [O0OOOO0OO0O0OOO00 ]for O0OOOO0OO0O0OOO00 in _OO0O00000OO0O000O ],np .int32 )#line:295
            cv2 .polylines (O0OO0O0OOOO000O00 ,[OOO0OOO000OO0OOOO ],True ,(177 ,206 ,251 ),2 )#line:296
            OO00OOO0OO0O0OOO0 =(0 ,255 ,0 )#line:297
            OOO0OOO000OO0OOOO =np .array ([OOOOO0OOO0OO0O0OO [O00OOO00O00O0OOOO ]for O00OOO00O00O0OOOO in _O00O0O0O00O0O000O ],np .int32 )#line:298
            cv2 .polylines (O0OO0O0OOOO000O00 ,[OOO0OOO000OO0OOOO ],True ,OO00OOO0OO0O0OOO0 ,2 )#line:299
            OOO0OOO000OO0OOOO =np .array ([OOOOO0OOO0OO0O0OO [OO0OO0OOO0O0O0000 ]for OO0OO0OOO0O0O0000 in _OOO0O00O000OO00OO ],np .int32 )#line:300
            cv2 .polylines (O0OO0O0OOOO000O00 ,[OOO0OOO000OO0OOOO ],False ,OO00OOO0OO0O0OOO0 ,2 )#line:301
            OOO0OOO000OO0OOOO =np .array ([OOOOO0OOO0OO0O0OO [O00O0OO0000OOOOO0 ]for O00O0OO0000OOOOO0 in _O00O0OO0OOO0OOOO0 ],np .int32 )#line:302
            cv2 .polylines (O0OO0O0OOOO000O00 ,[OOO0OOO000OO0OOOO ],False ,OO00OOO0OO0O0OOO0 ,2 )#line:303
            OO00OOO0OO0O0OOO0 =(255 ,0 ,0 )#line:304
            OOO0OOO000OO0OOOO =np .array ([OOOOO0OOO0OO0O0OO [O0000O0O00O0O0OO0 ]for O0000O0O00O0O0OO0 in _OO00O0O0OOOO00OO0 ],np .int32 )#line:305
            cv2 .polylines (O0OO0O0OOOO000O00 ,[OOO0OOO000OO0OOOO ],True ,OO00OOO0OO0O0OOO0 ,2 )#line:306
            OOO0OOO000OO0OOOO =np .array ([OOOOO0OOO0OO0O0OO [OOO0OOO0OOOO0O00O ]for OOO0OOO0OOOO0O00O in _OO0OOO0OOO00OO000 ],np .int32 )#line:307
            cv2 .polylines (O0OO0O0OOOO000O00 ,[OOO0OOO000OO0OOOO ],False ,OO00OOO0OO0O0OOO0 ,2 )#line:308
            OOO0OOO000OO0OOOO =np .array ([OOOOO0OOO0OO0O0OO [OO0000O00O0O00OO0 ]for OO0000O00O0O00OO0 in _O0OOOOO00O0000O0O ],np .int32 )#line:309
            cv2 .polylines (O0OO0O0OOOO000O00 ,[OOO0OOO000OO0OOOO ],False ,OO00OOO0OO0O0OOO0 ,2 )#line:310
            OO00OOO0OO0O0OOO0 =(0 ,0 ,255 )#line:311
            OOO0OOO000OO0OOOO =np .array ([OOOOO0OOO0OO0O0OO [OO00OOOO0OOOOOO0O ]for OO00OOOO0OOOOOO0O in _O0O0OOOO0OO00OO0O ],np .int32 )#line:312
            cv2 .polylines (O0OO0O0OOOO000O00 ,[OOO0OOO000OO0OOOO ],True ,OO00OOO0OO0O0OOO0 ,2 )#line:313
            OOO0OOO000OO0OOOO =np .array ([OOOOO0OOO0OO0O0OO [O00OOO0000000O00O ]for O00OOO0000000O00O in _O00OO00O000OO0O00 ],np .int32 )#line:314
            cv2 .polylines (O0OO0O0OOOO000O00 ,[OOO0OOO000OO0OOOO ],True ,OO00OOO0OO0O0OOO0 ,2 )#line:315
        return O0OO0O0OOOO000O00 #line:316
    def get_xy (OO00OO00O000O0OO0 ,id ='all'):#line:318
        OOO0O00000OO000OO =OO00OO00O000O0OO0 .get_xyz (id )#line:319
        if OOO0O00000OO000OO is None :return None #line:320
        if OOO0O00000OO000OO .ndim ==1 :#line:321
            return OOO0O00000OO000OO [:2 ]#line:322
        elif OOO0O00000OO000OO .ndim ==2 :#line:323
            return OOO0O00000OO000OO [:,:2 ]#line:324
        return None #line:325
    def get_xyz (OOOO00OO0O000OO0O ,id ='all'):#line:327
        if isinstance (id ,(int ,float )):#line:328
            id =int (id )#line:329
            if id <0 or id >467 :return None #line:330
            if OOOO00OO0O000OO0O ._landmarks is None :return None #line:331
            return OOOO00OO0O000OO0O ._landmarks [id ]#line:332
        elif isinstance (id ,str ):#line:333
            id =id .lower ()#line:334
            if id =='all':#line:335
                return OOOO00OO0O000OO0O ._landmarks #line:336
            elif id in OOOO00OO0O000OO0O ._points :#line:337
                return OOOO00OO0O000OO0O ._points [id ]#line:338
        return None #line:339
    def get_box (OOO0OOOO000O000OO ,id ='all'):#line:341
        if isinstance (id ,str ):#line:342
            id =id .lower ()#line:343
            if id =='all':#line:344
                return OOO0OOOO000O000OO ._boxes #line:345
            elif id in OOO0OOOO000O000OO ._boxes :#line:346
                return OOO0OOOO000O000OO ._boxes [id ]#line:347
        return None #line:348
    def get_width (OOOOO000000OO0OOO ,id ='all'):#line:350
        if isinstance (id ,str ):#line:351
            id =id .lower ()#line:352
            if id =='all':#line:353
                return OOOOO000000OO0OOO ._widths #line:354
            elif id in OOOOO000000OO0OOO ._widths :#line:355
                return OOOOO000000OO0OOO ._widths [id ]#line:356
        return 0 #line:357
    def get_height (O0000O0OOOOO0O0OO ,id ='all'):#line:359
        if isinstance (id ,str ):#line:360
            id =id .lower ()#line:361
            if id =='all':#line:362
                return O0000O0OOOOO0O0OO ._heights #line:363
            elif id in O0000O0OOOOO0O0OO ._heights :#line:364
                return O0000O0OOOOO0O0OO ._heights [id ]#line:365
        return 0 #line:366
    def get_area (O0O000O0O0OOOOOO0 ,id ='all'):#line:368
        if isinstance (id ,str ):#line:369
            id =id .lower ()#line:370
            if id =='all':#line:371
                return O0O000O0O0OOOOOO0 ._areas #line:372
            elif id in O0O000O0O0OOOOOO0 ._areas :#line:373
                return O0O000O0O0OOOOOO0 ._areas [id ]#line:374
        return 0 #line:375
    def get_orientation (OOO0O0OOOOOOOO0O0 ,degree =False ):#line:377
        O00OO0O00OO0O0000 =OOO0O0OOOOOOOO0O0 .get_xyz ('left eye')#line:378
        O00OO00OO00OO0OO0 =OOO0O0OOOOOOOO0O0 .get_xyz ('right eye')#line:379
        if degree :#line:380
            return Util .degree (O00OO0O00OO0O0000 ,O00OO00OO00OO0OO0 )#line:381
        else :#line:382
            return Util .radian (O00OO0O00OO0O0000 ,O00OO00OO00OO0OO0 )#line:383
    def get_feature (O0000O000O0O00O0O ,filter ='all'):#line:385
        OOOO0O0OOO000O00O =O0000O000O0O00O0O .get_width ('face')#line:386
        O0000O000OOO00O00 =O0000O000O0O00O0O .get_height ('face')#line:387
        OOO00OOO00OO00O00 =[OOOO0O0OOO000O00O ,O0000O000OOO00O00 ]#line:388
        if OOOO0O0OOO000O00O >0 and O0000O000OOO00O00 >0 :#line:389
            OOOOOOOOO0000000O =O0000O000O0O00O0O ._landmarks #line:390
            if OOOOOOOOO0000000O is not None :#line:391
                OO00OO0O00O0O0OOO =O0000O000O0O00O0O .get_xy ('face')#line:392
                OOOOOOOOO0000000O =(OOOOOOOOO0000000O [:,:2 ]-OO00OO0O00O0O0OOO )/OOO00OOO00OO00O00 #line:393
                O0O0O0O0OO00OO00O =OOOOOOOOO0000000O .reshape (-1 )#line:394
                if isinstance (filter ,str ):#line:395
                    filter =filter .lower ()#line:396
                    if filter =='all':#line:397
                        return O0O0O0O0OO00OO00O #line:398
                    elif filter in _OOO000000000OO000 :#line:399
                        O0OO0000O0OO00OO0 =_OOO000000000OO000 [filter ]#line:400
                        return np .array ([O0O0O0O0OO00OO00O [OOO0O0000O0OOO0OO ]for OOO0O0000O0OOO0OO in O0OO0000O0OO00OO0 ])#line:401
                elif isinstance (filter ,(list ,tuple )):#line:402
                    O0OO0000O0OO00OO0 =[]#line:403
                    for O0000O0000OOO0000 in filter :#line:404
                        if O0000O0000OOO0000 in _OOO000000000OO000 :#line:405
                            O0OO0000O0OO00OO0 .extend (_OOO000000000OO000 [O0000O0000OOO0000 ])#line:406
                    return np .array ([O0O0O0O0OO00OO00O [OOO0O0OO00O00OO0O ]for OOO0O0OO00O00OO0O in O0OO0000O0OO00OO0 ])#line:407
        return None #line:408
    def _get_feature_label (O0000OO0O00OOOOO0 ,filter ='all'):#line:410
        if isinstance (filter ,str ):#line:411
            filter =filter .lower ()#line:412
            if filter =='all':#line:413
                return ['f'+str (O0OOO0000O0OO00OO )for O0OOO0000O0OO00OO in range (468 )]#line:414
            elif filter in _OOO000000000OO000 :#line:415
                OOOOO0000OOOOOO0O =_OOO000000000OO000 [filter ]#line:416
                return ['f'+str (O00O0O0O000O0OOO0 )for O00O0O0O000O0OOO0 in OOOOO0000OOOOOO0O ]#line:417
        elif isinstance (filter ,(list ,tuple )):#line:418
            OOOOO0000OOOOOO0O =[]#line:419
            for OOOOOOO0000OO00OO in filter :#line:420
                if OOOOOOO0000OO00OO in _OOO000000000OO000 :#line:421
                    OOOOO0000OOOOOO0O .extend (_OOO000000000OO000 [OOOOOOO0000OO00OO ])#line:422
            return ['f'+str (O00OOO0O00O00OOOO )for O00OOO0O00O00OOOO in OOOOO0000OOOOOO0O ]#line:423
    def record_feature (O0OOO0OO00OOOOOOO ,OO00O000O000O0OOO ,OO00O00O0OO0O000O ,filter ='all',interval_msec =100 ,frames =20 ,countdown =3 ):#line:425
        if countdown >0 :#line:426
            OO00O000O000O0OOO .count_down (countdown )#line:427
        OO00O000OOO00OOOO =0 #line:428
        OO0OOOO00OO00O00O =timer ()#line:429
        OOOO0O00OO0O00OO0 =','.join (O0OOO0OO00OOOOOOO ._get_feature_label (filter ))#line:430
        OOO0OOOO00000O00O =[]#line:431
        while True :#line:432
            if OO00O000OOO00OOOO >=frames :break #line:433
            O0O00O000O0O00OOO =OO00O000O000O0OOO .read ()#line:434
            if O0OOO0OO00OOOOOOO .detect (O0O00O000O0O00OOO ):#line:435
                O0O00O000O0O00OOO =O0OOO0OO00OOOOOOO .draw_result (O0O00O000O0O00OOO )#line:436
                if timer ()>OO0OOOO00OO00O00O :#line:437
                    OOO0OOOO00000O00O .append (O0OOO0OO00OOOOOOO .get_feature (filter ))#line:438
                    OO00O000OOO00OOOO +=1 #line:439
                    print ('saved',OO00O000OOO00OOOO )#line:440
                    OO0OOOO00OO00O00O +=interval_msec /1000.0 #line:441
                if OO00O000O000O0OOO .check_key ()=='esc':#line:442
                    return #line:443
            OO00O000O000O0OOO .show (O0O00O000O0O00OOO )#line:444
        if OO00O00O0OO0O000O is not None :#line:445
            Util .realize_filepath (OO00O00O0OO0O000O )#line:446
            np .savetxt (OO00O00O0OO0O000O ,OOO0OOOO00000O00O ,fmt ='%f',delimiter =',',header =OOOO0O00OO0O00OO0 ,comments ='')#line:447
    @staticmethod #line:449
    def distance (OO000OOO00OO00OOO ,OO0O0O0O0OOOO0O0O ):#line:450
        return Util .distance (OO000OOO00OO00OOO ,OO0O0O0O0OOOO0O0O )#line:451
    @staticmethod #line:453
    def degree (O0OO00O0000O0OO0O ,OO0000OO0O0000OOO ):#line:454
        return Util .degree (O0OO00O0000O0OO0O ,OO0000OO0O0000OOO )#line:455
    @staticmethod #line:457
    def radian (OOO0O0OO0O0O0O00O ,OO0000000OO0O00OO ):#line:458
        return Util .radian (OOO0O0OO0O0O0O00O ,OO0000000OO0O00OO )#line:459
