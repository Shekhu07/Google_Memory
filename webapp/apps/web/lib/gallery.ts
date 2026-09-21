/** The committed manifest written by engine/export_web.py's build_gallery(). */
export type GalleryPhoto = { f: string; t: string };
export type GallerySection = { month: string; label: string; photos: GalleryPhoto[] };
export type Gallery = { count: number; built: string; sections: GallerySection[] };
