# from .Ruangan import Ruangan
# from .MatKul import MatKul
# from .MatKulOnlyTime import MatKulOnlyTime

require 'ruangan'
require 'mat_kul'
require 'matkul_only_time'

class Jadwal
  @daftar_ruangan = []
  @daftar_mata_kuliah = []
  @total_pasangan = 0

  def process_ruangan_dan_mata_kuliah(ruangan_raw, mata_kuliah_raw)
    idruangan = 0
    for ruangan in ruangan_raw
      temp = ruangan.split(';')
      temp[3] = temp[3].split(',')
      for i in range(len(temp[3]))
        temp[3][i] = int(temp[3][i])
      end
      temp_ruangan = Ruangan(idruangan,temp[0], int(float(temp[1])), int(float(temp[2])), temp[3])
      idruangan += 1
      @daftar_ruangan.append(temp_ruangan)
    end

    idmatkul = 0
      for mata_kuliah in mata_kuliah_raw
        temp = mata_kuliah.split(';')
        temp[5] = temp[5].split(',')
        for i in range(len(temp[5]))
          temp[5][i] = int(temp[5][i])
        end
        temp_mata_kuliah = MatKul(idmatkul, temp[0], temp[1], int(float(temp[2])), int(float(temp[3])), int(temp[4]), temp[5])
        idmatkul += 1
        @daftar_mata_kuliah.append(temp_mata_kuliah)
      end

    n = len(@daftar_mata_kuliah)
    temp_total = 0
    for i in range(0,n)
      @total_pasangan += temp_total * @daftar_mata_kuliah[i].sks
      temp_total += @daftar_mata_kuliah[i].sks
    end
    @total_pasangan += 1
  end

  def read_file(ruangan_raw, mata_kuliah_raw, nama_file)
    f = open(nama_file, "r")
    mylist = f.read().splitlines()
    ruangan_loaded = False
    for line in mylist
      if (line == 'Ruangan' or line == '')
        break
      elsif (line == 'Jadwal')
        ruangan_loaded = True
      elsif (!ruangan_loaded)
        ruangan_raw.append(line)
      else
        mata_kuliah_raw.append(line)
      end
    end
    f.close()
  end

  def init_file(nama_file)
    ruangan_raw = []
    mata_kuliah_raw = []
    read_file(ruangan_raw, mata_kuliah_raw, nama_file)
    process_ruangan_dan_mata_kuliah(ruangan_raw, mata_kuliah_raw)
    end

  def initialize(nama_file)
    @daftar_ruangan = []
    @daftar_mata_kuliah = []
    init_file(nama_file)
  end

end

