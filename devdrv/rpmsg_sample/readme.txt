On Android:




run log:
<4>[91102.964294]  rpmsg client: init
<4>[91102.970855]  rpmsg client: probe
<6>[91102.980255] rpmsg_sample rpmsg3: new channel, src<->dst : 0x401 <-> 0x32!
<7>[91102.997283] rpmsg_virtio TX: 06 00 00 00 01 04 00 00 32 00 00 00 00 00 00 00  ........2......

<7>[91103.014099] rpmsg_virtio TX: 68 65 6c 6c 6f 20                                hello
<6>[91103.027191] omap-iommu omap-iommu.0: iommu_get: ducati qos_request
<4>[91103.050506] omap_hwmod: ipu: failed to hardreset
<6>[91103.061981] omap-iommu omap-iommu.0: ducati: version 2.1
<4>[91103.072357]  rpmsg client: probe
<6>[91103.081451] rpmsg_sample rpmsg4: new channel, src<->dst : 0x402 <-> 0x33!
<7>[91103.089538] rpmsg_virtio TX: 06 00 00 00 02 04 00 00 33 00 00 00 00 00 00 00  ........3......

<7>[91103.106658] rpmsg_virtio TX: 68 65 6c 6c 6f 20                                hello
<7>[91103.435363] rpmsg_virtio RX: 06 00 00 00 32 00 00 00 01 04 00 00 00 00 00 00  ....2..........

<7>[91103.445281] rpmsg_virtio RX: 68 65 6c 6c 6f 20                                hello
<6>[91103.466156] rpmsg_sample rpmsg3: incoming msg 1 (src: 0x32)
<7>[91103.472747] rpmsg_sample_cb68 65 6c 6c 6f 20                                hello
<7>[91103.495147] rpmsg_virtio TX: 08 00 00 00 01 04 00 00 32 00 00 00 00 00 00 00  ........2......

<7>[91103.511718] rpmsg_virtio TX: 68 65 6c 6c 6f 20 20 31                          hello  1
<7>[91103.511718] rpmsg_virtio RX: 06 00 00 00 33 00 00 00 02 04 00 00 00 00 00 00  ....3..........

<7>[91103.537780] rpmsg_virtio RX: 68 65 6c 6c 6f 20                                hello
<6>[91103.553558] rpmsg_sample rpmsg4: incoming msg 2 (src: 0x33)
<7>[91103.553558] rpmsg_sample_cb68 65 6c 6c 6f 20                                hello
<7>[91103.579406] rpmsg_virtio TX: 08 00 00 00 02 04 00 00 33 00 00 00 00 00 00 00  ........3......

<7>[91103.596710] rpmsg_virtio TX: 68 65 6c 6c 6f 20 20 32                          hello  2
<7>[91103.613342] rpmsg_virtio RX: 08 00 00 00 32 00 00 00 01 04 00 00 00 00 00 00  ....2..........

<7>[91103.629821] rpmsg_virtio RX: 68 65 6c 6c 6f 20 20 31                          hello  1
<6>[91103.645904] rpmsg_sample rpmsg3: incoming msg 3 (src: 0x32)
<7>[91103.656799] rpmsg_sample_cb68 65 6c 6c 6f 20 20 31                          hello  1
<7>[91103.672241] rpmsg_virtio TX: 08 00 00 00 01 04 00 00 32 00 00 00 00 00 00 00  ........2......

<7>[91103.689392] rpmsg_virtio TX: 68 65 6c 6c 6f 20 20 33                          hello  3
<7>[91103.712951] rpmsg_virtio RX: 08 00 00 00 33 00 00 00 02 04 00 00 00 00 00 00  ....3..........

<7>[91103.729553] rpmsg_virtio RX: 68 65 6c 6c 6f 20 20 32                          hello  2
<6>[91103.729888] rpmsg_sample rpmsg4: incoming msg 4 (src: 0x33)
<7>[91103.729888] rpmsg_sample_cb68 65 6c 6c 6f 20 20 32                          hello  2
<7>[91103.772766] rpmsg_virtio TX: 08 00 00 00 02 04 00 00 33 00 00 00 00 00 00 00  ........3......

<7>[91103.782257] rpmsg_virtio TX: 68 65 6c 6c 6f 20 20 34                          hello  4
<7>[91103.798095] rpmsg_virtio RX: 08 00 00 00 32 00 00 00 01 04 00 00 00 00 00 00  ....2..........

<7>[91103.822448] rpmsg_virtio RX: 68 65 6c 6c 6f 20 20 33                          hello  3
<6>[91103.831665] rpmsg_sample rpmsg3: incoming msg 5 (src: 0x32)
<7>[91103.831665] rpmsg_sample_cb68 65 6c 6c 6f 20 20 33                          hello  3
<7>[91103.857849] rpmsg_virtio TX: 08 00 00 00 01 04 00 00 32 00 00 00 00 00 00 00  ........2......

<7>[91103.875152] rpmsg_virtio TX: 68 65 6c 6c 6f 20 20 35                          hello  5
<7>[91103.875152] rpmsg_virtio RX: 08 00 00 00 33 00 00 00 02 04 00 00 00 00 00 00  ....3..........

<7>[91103.915161] rpmsg_virtio RX: 68 65 6c 6c 6f 20 20 34                          hello  4
<6>[91103.923919] rpmsg_sample rpmsg4: incoming msg 6 (src: 0x33)
<7>[91103.935119] rpmsg_sample_cb68 65 6c 6c 6f 20 20 34                          hello  4
<7>[91103.958343] rpmsg_virtio TX: 08 00 00 00 02 04 00 00 33 00 00 00 00 00 00 00  ........3......

<7>[91103.958343] rpmsg_virtio TX: 68 65 6c 6c 6f 20 20 36                          hello  6
<7>[91103.987701] rpmsg_virtio RX: 08 00 00 00 32 00 00 00 01 04 00 00 00 00 00 00  ....2..........

<7>[91104.018707] rpmsg_virtio RX: 68 65 6c 6c 6f 20 20 35                          hello  5
<6>[91104.018707] rpmsg_sample rpmsg3: incoming msg 7 (src: 0x32)
<7>[91104.057769] rpmsg_sample_cb68 65 6c 6c 6f 20 20 35                          hello  5
<7>[91104.087432] rpmsg_virtio TX: 08 00 00 00 01 04 00 00 32 00 00 00 00 00 00 00  ........2......

<7>[91104.120544] rpmsg_virtio TX: 68 65 6c 6c 6f 20 20 37                          hello  7
<7>[91104.142425] rpmsg_virtio RX: 08 00 00 00 33 00 00 00 02 04 00 00 00 00 00 00  ....3..........

<7>[91104.159667] rpmsg_virtio RX: 68 65 6c 6c 6f 20 20 36                          hello  6
<6>[91104.168884] rpmsg_sample rpmsg4: incoming msg 8 (src: 0x33)
<7>[91104.185516] rpmsg_sample_cb68 65 6c 6c 6f 20 20 36                          hello  6
<7>[91104.198883] rpmsg_virtio TX: 08 00 00 00 02 04 00 00 33 00 00 00 00 00 00 00  ........3......

<7>[91104.214080] rpmsg_virtio TX: 68 65 6c 6c 6f 20 20 38                          hello  8
<7>[91104.237731] rpmsg_virtio RX: 08 00 00 00 32 00 00 00 01 04 00 00 00 00 00 00  ....2..........

<7>[91104.253356] rpmsg_virtio RX: 68 65 6c 6c 6f 20 20 37                          hello  7
<6>[91104.265136] rpmsg_sample rpmsg3: incoming msg 9 (src: 0x32)
<7>[91104.276794] rpmsg_sample_cb68 65 6c 6c 6f 20 20 37                          hello  7
<7>[91104.297851] rpmsg_virtio TX: 08 00 00 00 01 04 00 00 32 00 00 00 00 00 00 00  ........2......

<7>[91104.313079] rpmsg_virtio TX: 68 65 6c 6c 6f 20 20 39                          hello  9
<7>[91104.331542] rpmsg_virtio RX: 08 00 00 00 33 00 00 00 02 04 00 00 00 00 00 00  ....3..........

<7>[91104.347686] rpmsg_virtio RX: 68 65 6c 6c 6f 20 20 38                          hello  8
<6>[91104.368011] rpmsg_sample rpmsg4: incoming msg 10 (src: 0x33)
<7>[91104.378448] rpmsg_sample_cb68 65 6c 6c 6f 20 20 38                          hello  8
<6>[91104.393432] rpmsg_sample rpmsg4: goodbye!
<7>[91104.405944] rpmsg_virtio RX: 08 00 00 00 32 00 00 00 01 04 00 00 00 00 00 00  ....2..........

<7>[91104.415405] rpmsg_virtio RX: 68 65 6c 6c 6f 20 20 39                          hello  9
<6>[91104.433044] rpmsg_sample rpmsg3: incoming msg 11 (src: 0x32)
<7>[91104.448699] rpmsg_sample_cb68 65 6c 6c 6f 20 20 39                          hello  9
<6>[91104.459289] rpmsg_sample rpmsg3: goodbye!
