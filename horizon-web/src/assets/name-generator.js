const birds = [
  'Robin',
  'Hawk',
  'Crane',
  'Merle',
  'Wren',
  'Phoenix',
  'Sparrow',
  'Swift',
  'Byrd',
  'Falcon',
  'Gull',
  'Eagle',
  'Finch',
  'Chelidon',
  'Corvus',
  'Corbin',
  'Bran',
  'Fechine',
  'Wulfram',
  'Colm',
  'Callum',
  'Heron',
  'Jay',
  'Columba',
  'Lonan',
  'Manu',
  'Talon',
  'Nesta',
  'Nestor',
  'Altair',
  'Culver',
  'Efron',
  'Faulkner',
  'Vireo',
  'Gawain',
  'Griffon',
  'Shahaf',
  'Akos',
  'Horus',
  'Merlin',
  'Hula',
  'Arvid',
  'Arnold',
  'Whistler',
  'Jonah',
  'Ava',
  'Gannet',
  'Teal',
  'Sarika',
  'Aya',
  'Deryn',
  'Rhea',
  'Starling',
  'Swan',
  'Circe',
  'Loa',
  'Jarita',
  'Sephora',
  'Luscinia',
  'Philomela',
  'Dove',
  'Laraline',
  'Kestrel',
  'Drora',
  'Alouette',
  'Jemima',
  'Parastoo',
  'Celandine',
  'Branwen',
  'Paloma',
  'Avis',
  'Aderyn',
  'Lark',
  'Tori',
  'Birdie',
  'Raven',
  'Phoebe',
  'Chenoa',
  'Jaret',
  'Aghavni',
  'Usoa',
  'Morrigan',
  'Faigel',
  'Einin',
  'Jae',
  'Evelyn',
  'Oriole',
  'Palila',
  'Bird',
  'Feather',
  'Nydia',
  'Yonina',
  'Zippora',
  'Linnet',
  'Branwen',
  'Rosella',
  'Weaver',
  'Gwylan',
  'Gwennol',
  'Suzume',
  'Halcyon'
]

const colors = [
  'Sarcoline',
  'Coquelicot',
  'Smaragdine',
  'Mikado',
  'Glaucous',
  'Wenge',
  'Fulvous',
  'Xanadu',
  'Falu',
  'Eburnean',
  'Amaranth',
  'Smalt',
  'Byzantium',
  'Cordovan',
  'Vermilion',
  'Sienna',
  'Gamboge',
  'Fulvous',
  'Pavo',
  'Verdigris',
  'Aubergine',
  'Lichen',
  'Malachite',
  'Aureolin',
  'Bole',
  'Fallow'
]

export function getRandomName () {
  const bird = birds[Math.floor(Math.random() * birds.length)]
  const color = colors[Math.floor(Math.random() * colors.length)]
  const suffix = ((+new Date()) + Math.random() * 100).toString(32).substring(0, 5)

  return [color, bird, suffix].join('').substring(0, 30)
}
